from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models import Story, Country, Article, Claim, StoryArticle, Source
from ..schemas import NewsFeedResponse, StoryOut, ArticleOut, ClaimOut, EvidenceOut, VerificationReviewOut, AIAnalysisOut
from ..services.ai_detector_service import analyze_fake_news_and_credibility

router = APIRouter(tags=["News Feeds"])

def format_story_response(story: Story) -> StoryOut:
    articles_out = []
    primary_source_name = None
    
    for assoc in story.articles:
        art = assoc.article
        pub_name = art.source.name if art.source else "Unknown Source"
        if not primary_source_name:
            primary_source_name = pub_name
        articles_out.append(ArticleOut(
            id=art.id,
            source_id=art.source_id,
            publisher_name=pub_name,
            canonical_url=art.canonical_url,
            title=art.title,
            excerpt=art.excerpt,
            full_content=art.full_content,
            image_url=art.image_url,
            language=art.language,
            published_at=art.published_at,
            fetched_at=art.fetched_at
        ))

    claims_out = []
    verified_count = 0
    for cl in story.claims:
        if cl.claim_status == "corroborated":
            verified_count += 1
            
        evidence_list = [
            EvidenceOut(
                id=ev.id,
                claim_id=ev.claim_id,
                source_url=ev.source_url,
                source_name=ev.source_name,
                evidence_type=ev.evidence_type,
                stance=ev.stance,
                excerpt=ev.excerpt,
                independence_group=ev.independence_group,
                retrieved_at=ev.retrieved_at
            )
            for ev in cl.evidence_items
        ]
        
        reviews_list = [
            VerificationReviewOut(
                id=rv.id,
                claim_id=rv.claim_id,
                reviewer_name=rv.reviewer_name,
                decision=rv.decision,
                rationale=rv.rationale,
                policy_version=rv.policy_version,
                created_at=rv.created_at
            )
            for rv in cl.reviews
        ]

        claims_out.append(ClaimOut(
            id=cl.id,
            story_id=cl.story_id,
            claim_text=cl.claim_text,
            context=cl.context,
            claim_status=cl.claim_status,
            extracted_at=cl.extracted_at,
            evidence_items=evidence_list,
            reviews=reviews_list
        ))

    # Collect unique corroborating source names
    source_names = []
    for sa in story.articles:
        if sa.article and sa.article.source:
            sname = sa.article.source.name
            if sname not in source_names:
                source_names.append(sname)
    if not source_names and primary_source_name:
        source_names.append(primary_source_name)

    ai_data = analyze_fake_news_and_credibility(
        title=story.display_title,
        content=story.full_content or story.summary or "",
        source_name=primary_source_name,
        articles_count=len(story.articles),
        corroborating_sources=source_names
    )
    ai_analysis = AIAnalysisOut(
        credibility_score=ai_data["credibility_score"],
        verdict=ai_data["verdict"],
        verdict_label=ai_data["verdict_label"],
        verdict_color=ai_data["verdict_color"],
        sensationalism_score=ai_data["sensationalism_score"],
        attribution_score=ai_data["attribution_score"],
        corroboration_sources_count=ai_data["corroboration_sources_count"],
        signals=ai_data["signals"],
        recommendation=ai_data["recommendation"],
        source_names=source_names,
        is_multi_source=len(source_names) > 1
    )

    return StoryOut(
        id=story.id,
        display_title=story.display_title,
        topic=story.topic,
        state=story.state,
        country_iso2=story.country_iso2,
        first_seen_at=story.first_seen_at,
        updated_at=story.updated_at,
        summary=story.summary,
        full_content=story.full_content,
        image_url=story.image_url,
        articles_count=len(story.articles),
        claims_count=len(story.claims),
        verified_claims_count=verified_count,
        primary_source=primary_source_name,
        articles=articles_out,
        claims=claims_out,
        ai_analysis=ai_analysis
    )

from datetime import datetime, timezone, timedelta
from ..services.live_news_engine import inject_next_live_story

@router.get("/news", response_model=NewsFeedResponse)
def get_news_feed(
    country: str = Query("NP", description="Country ISO2 code (e.g., NP, US, CA)"),
    feed: str = Query("latest", pattern="^(latest|verified|history)$", description="'latest', 'verified', or 'history'"),
    topic: Optional[str] = Query(None, description="Topic filter (e.g. politics, business, weather)"),
    q: Optional[str] = Query(None, description="Search query"),
    archive_date: Optional[str] = Query(None, description="Specific date for history feed (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Returns news feeds partitioned by 48-hour active window vs historical archives:
    - Latest: Live rapid, attributed reports within the last 48 hours (auto-updates dynamically).
    - Verified: Factually corroborated stories within the last 48 hours.
    - History: Archived past stories older than 48 hours.
    """
    c = country.upper()
    now_utc = datetime.now(timezone.utc)
    cutoff_48h = now_utc - timedelta(hours=48)

    # Auto-inject dynamic live story if Nepal feed is accessed and newest story is older than 25s
    if c == "NP" and feed in ["latest", "verified"]:
        try:
            inject_next_live_story(db, force=False)
        except Exception as e:
            print(f"Notice: live story injection skipped: {e}")

    query = db.query(Story).filter(Story.country_iso2 == c)

    if feed == "history":
        # Stories older than 48 hours move to the history archive
        query = query.filter(Story.first_seen_at < cutoff_48h)
        if archive_date:
            try:
                target_date = datetime.strptime(archive_date, "%Y-%m-%d").date()
                query = query.filter(Story.first_seen_at >= datetime(target_date.year, target_date.month, target_date.day, 0, 0, 0, tzinfo=timezone.utc))
                query = query.filter(Story.first_seen_at < datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=timezone.utc))
            except ValueError:
                pass
    elif feed == "verified":
        # Active verified stories from the last 48 hours
        query = query.filter(Story.first_seen_at >= cutoff_48h)
        query = query.filter(Story.state == "verified_summary")
    else:
        # Latest active feed within the last 48 hours
        query = query.filter(Story.first_seen_at >= cutoff_48h)
        query = query.filter(Story.state.in_(["developing", "under_review", "verified_summary", "corrected"]))

    if topic and topic.lower() != "all":
        query = query.filter(Story.topic == topic.lower())

    if q:
        search_term = f"%{q}%"
        query = query.filter(Story.display_title.ilike(search_term))

    stories = query.order_by(Story.first_seen_at.desc()).all()
    items = [format_story_response(s) for s in stories]

    return NewsFeedResponse(
        country=c,
        feed=feed,
        topic=topic,
        total=len(items),
        items=items
    )


@router.post("/news/refresh-live", response_model=StoryOut)
def refresh_live_feed(
    country: str = Query("NP", description="Country ISO2 code"),
    db: Session = Depends(get_db)
):
    """
    Manually triggers an instant live story injection from RONB/Setopati/OnlineKhabar.
    Guarantees a brand-new breaking story is generated immediately.
    """
    c = country.upper()
    if c != "NP":
        story = db.query(Story).filter(Story.country_iso2 == c).first()
        if not story:
            raise HTTPException(status_code=404, detail="No stories for country")
        return format_story_response(story)

    new_story = inject_next_live_story(db, force=True)
    if not new_story:
        new_story = db.query(Story).filter(Story.country_iso2 == "NP").order_by(Story.first_seen_at.desc()).first()
    return format_story_response(new_story)
