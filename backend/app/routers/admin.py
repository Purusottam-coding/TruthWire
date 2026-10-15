from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from ..database import get_db
from ..models import Source, Claim, Story, VerificationReview, StatusHistory, Evidence
from ..schemas import SourceOut, SourceCreate, ClaimOut, ReviewSubmission, VerificationReviewOut, StoryCorrection
from .news import format_story_response

router = APIRouter(prefix="/admin", tags=["Admin & Review Queue"])

@router.get("/sources", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    """List all registered news sources with license notes and health status."""
    return db.query(Source).all()

@router.post("/sources", response_model=SourceOut)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    new_src = Source(**payload.dict())
    db.add(new_src)
    db.commit()
    db.refresh(new_src)
    return new_src

@router.patch("/sources/{source_id}", response_model=SourceOut)
def toggle_source(source_id: str, active: Optional[bool] = Body(None, embed=True), db: Session = Depends(get_db)):
    src = db.query(Source).filter(Source.id == source_id).first()
    if not src:
        raise HTTPException(status_code=404, detail="Source not found")
    if active is not None:
        src.active = active
        db.commit()
        db.refresh(src)
    return src

@router.get("/review-queue", response_model=List[ClaimOut])
def get_review_queue(
    country: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns unverified and checking claims waiting for editorial review.
    Claims can be filtered by country.
    """
    query = db.query(Claim).join(Story).filter(
        Claim.claim_status.in_(["unverified", "checking", "disputed"])
    )
    if country:
        query = query.filter(Story.country_iso2 == country.upper())
    
    claims = query.order_by(Claim.extracted_at.desc()).all()
    
    # We reuse format_story_response claims structure
    result = []
    for cl in claims:
        evidence_list = [
            {
                "id": ev.id,
                "claim_id": ev.claim_id,
                "source_url": ev.source_url,
                "source_name": ev.source_name,
                "evidence_type": ev.evidence_type,
                "stance": ev.stance,
                "excerpt": ev.excerpt,
                "independence_group": ev.independence_group,
                "retrieved_at": ev.retrieved_at
            }
            for ev in cl.evidence_items
        ]
        reviews_list = [
            {
                "id": rv.id,
                "claim_id": rv.claim_id,
                "reviewer_name": rv.reviewer_name,
                "decision": rv.decision,
                "rationale": rv.rationale,
                "policy_version": rv.policy_version,
                "created_at": rv.created_at
            }
            for rv in cl.reviews
        ]
        result.append(ClaimOut(
            id=cl.id,
            story_id=cl.story_id,
            claim_text=cl.claim_text,
            context=cl.context,
            claim_status=cl.claim_status,
            extracted_at=cl.extracted_at,
            evidence_items=evidence_list,
            reviews=reviews_list
        ))
    return result

@router.post("/claims/{claim_id}/review", response_model=VerificationReviewOut)
def submit_claim_review(
    claim_id: str,
    submission: ReviewSubmission,
    db: Session = Depends(get_db)
):
    """
    Submits a factual verification review for a claim.
    If the claim is promoted to verified and is corroborated,
    checks if all key claims for the parent story are verified,
    and upgrades parent story state to 'verified_summary'.
    """
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    old_claim_status = claim.claim_status
    
    # Map decision to claim status
    status_map = {
        "promoted_to_verified": "corroborated",
        "marked_corroborated": "corroborated",
        "flagged_as_disputed": "disputed",
        "flagged_as_refuted": "refuted",
        "marked_inconclusive": "inconclusive"
    }
    new_claim_status = status_map.get(submission.decision, "checking")
    claim.claim_status = new_claim_status

    # Record review decision
    rev = VerificationReview(
        claim_id=claim.id,
        reviewer_name=submission.reviewer_name,
        decision=submission.decision,
        rationale=submission.rationale,
        policy_version=submission.policy_version
    )
    db.add(rev)

    # Record status history audit
    history = StatusHistory(
        entity_type="claim",
        entity_id=claim.id,
        old_status=old_claim_status,
        new_status=new_claim_status,
        actor=submission.reviewer_name,
        reason=submission.rationale
    )
    db.add(history)

    # Check parent story promotion
    story = claim.story
    if story:
        all_claims = story.claims
        # If at least one claim is corroborated and none refuted
        corroborated_count = sum(1 for c in all_claims if c.claim_status == "corroborated")
        has_refuted = any(c.claim_status == "refuted" for c in all_claims)

        if submission.decision == "promoted_to_verified" and not has_refuted:
            old_story_state = story.state
            story.state = "verified_summary"
            story.updated_at = datetime.now(timezone.utc)
            db.add(StatusHistory(
                entity_type="story",
                entity_id=story.id,
                old_status=old_story_state,
                new_status="verified_summary",
                actor=submission.reviewer_name,
                reason=f"Promoted to verified feed following review of claim {claim.id}"
            ))

    db.commit()
    db.refresh(rev)
    return rev

@router.post("/stories/{story_id}/correction")
def apply_story_correction(
    story_id: str,
    correction: StoryCorrection,
    db: Session = Depends(get_db)
):
    """
    Applies an editorial correction or retraction to a story.
    Appends to immutable audit trail, never quietly overwriting history.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    old_state = story.state
    story.state = correction.new_state
    if correction.new_summary:
        story.summary = correction.new_summary
    story.updated_at = datetime.now(timezone.utc)

    history = StatusHistory(
        entity_type="story",
        entity_id=story.id,
        old_status=old_state,
        new_status=correction.new_state,
        actor=correction.actor,
        reason=correction.reason
    )
    db.add(history)
    db.commit()

    return {"message": "Correction recorded successfully", "new_state": story.state}
