from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from ..database import get_db
from ..models import Story
from ..schemas import AIScanRequest, AIScanResponse
from ..services.ai_detector_service import (
    analyze_fake_news_and_credibility,
    find_matching_story,
    calculate_semantic_similarity,
    verify_claim_against_live_websites
)

router = APIRouter(prefix="/ai", tags=["AI Duplicate & Fake News Detector"])

@router.post("/scan", response_model=AIScanResponse)
def scan_news_for_fake_news_and_duplicates(
    payload: AIScanRequest,
    db: Session = Depends(get_db)
):
    """
    AI Duplicate & Fake News Detector Endpoint:
    1. Actively visits top authentic news websites (OnlineKhabar, Setopati, Kathmandu Post)
       to verify if the claim is published or a rumor, and updates the database accordingly.
    2. Evaluates text for sensationalism, rumor patterns, and institutional attribution.
    3. Produces a credibility score, verdict, visited websites log, and actionable advice.
    """
    input_text = payload.text.strip()
    input_title = (payload.title or input_text[:120]).strip()
    if not input_text:
        raise HTTPException(status_code=400, detail="Text to analyze cannot be empty.")

    # 1. Active Live Website Cross-Verification (visits OnlineKhabar, Setopati, TKP, and updates DB)
    live_web_result = verify_claim_against_live_websites(input_text, db)

    # 2. Check for duplicates in active database
    match_result = find_matching_story(db, input_title, input_text, country_iso2="NP", threshold=0.48)
    is_duplicate = False
    matched_id = None
    matched_title = None
    sim_score = None
    corrob_sources = []

    if match_result:
        matched_story, sim_score = match_result
        is_duplicate = True
        matched_id = matched_story.id
        matched_title = matched_story.display_title
        corrob_sources = [sa.article.source.name for sa in matched_story.articles if sa.article and sa.article.source]

    # Add any matched sources from live visited websites
    for ma in live_web_result.get("matched_articles", []):
        if ma.get("source") and ma["source"] not in corrob_sources:
            corrob_sources.append(ma["source"])

    # 3. Analyze fake news & credibility signals
    ai_result = analyze_fake_news_and_credibility(
        title=input_title,
        content=input_text,
        source_name="Live Web & User Scan",
        articles_count=len(corrob_sources) if corrob_sources else 1,
        corroborating_sources=corrob_sources
    )

    signals = list(ai_result["signals"])

    if live_web_result["is_verified_on_web"]:
        signals.insert(0, f"✓ Live Website Verification: Found active reporting across {live_web_result['matched_articles_count']} authentic news outlet(s).")
        verdict = "AUTHENTIC_VERIFIED"
        verdict_label = "Authentic & Verified on Live Websites"
        verdict_color = "emerald"
        credibility_score = max(ai_result["credibility_score"], 88)
        recommendation = live_web_result["recommendation"]
    elif ai_result["sensationalism_score"] > 35:
        signals.insert(0, "⚠️ Live Website Verification: 0 authentic news portals (OnlineKhabar, Setopati, TKP) reported this event.")
        verdict = "UNVERIFIED_RUMOR"
        verdict_label = "Unconfirmed Rumor / Clickbait"
        verdict_color = "rose"
        credibility_score = min(ai_result["credibility_score"], 40)
        recommendation = "Live website search confirmed no authentic reporting. Classified as unverified rumor."
    else:
        signals.insert(0, "ℹ️ Live Website Verification: No immediate breaking reports found across monitored portals.")
        verdict = ai_result["verdict"]
        verdict_label = ai_result["verdict_label"]
        verdict_color = ai_result["verdict_color"]
        credibility_score = ai_result["credibility_score"]
        recommendation = ai_result["recommendation"]

    if is_duplicate:
        signals.append(f"✓ AI Duplicate Match ({sim_score*100:.1f}%): Corroborates active story '{matched_title}' in TruthWire database.")

    return AIScanResponse(
        text=input_text,
        credibility_score=credibility_score,
        verdict=verdict,
        verdict_label=verdict_label,
        verdict_color=verdict_color,
        sensationalism_score=ai_result["sensationalism_score"],
        attribution_score=ai_result["attribution_score"],
        signals=signals,
        recommendation=recommendation,
        is_duplicate=is_duplicate,
        duplicate_similarity_score=sim_score,
        matched_story_id=matched_id,
        matched_story_title=matched_title,
        visited_sites=live_web_result["visited_sites"],
        actions_taken=live_web_result["actions_taken"]
    )

@router.get("/story/{story_id}")
def get_story_ai_factcheck(story_id: str, db: Session = Depends(get_db)):
    """
    Returns granular AI Fact-Check & Verification Analysis for a specific Story.
    """
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found.")

    sources = [sa.article.source.name for sa in story.articles if sa.article and sa.article.source]
    ai_data = analyze_fake_news_and_credibility(
        title=story.display_title,
        content=story.full_content or story.summary or "",
        source_name=sources[0] if sources else "Wire Report",
        articles_count=len(story.articles),
        corroborating_sources=sources
    )
    return {
        "story_id": story.id,
        "display_title": story.display_title,
        "sources": sources,
        "is_multi_source": len(sources) > 1,
        **ai_data
    }
