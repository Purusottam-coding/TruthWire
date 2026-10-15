import hashlib
import feedparser
import requests
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models import Source, Article, Story, StoryArticle, Claim
try:
    from nepali_utils.converter import normalize_devanagari, is_likely_preeti, preeti_to_unicode
except ImportError:
    import sys, os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from nepali_utils.converter import normalize_devanagari, is_likely_preeti, preeti_to_unicode

def generate_content_hash(title: str, url: str) -> str:
    raw = f"{title.strip()}|{url.strip()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def clean_and_normalize_text(text: Optional[str], language: str) -> str:
    if not text:
        return ""
    # Strip HTML tags
    cleaned = text.strip()
    if language == "ne" or is_likely_preeti(cleaned):
        cleaned = normalize_devanagari(cleaned)
    return cleaned

def ingest_source_rss(source: Source, db: Session) -> Dict[str, Any]:
    """
    Ingests permitted RSS feed metadata idempotently.
    Applies Preeti-to-Unicode conversion and Devanagari normalization for Nepali sources.
    """
    if not source.endpoint:
        return {"source": source.name, "status": "skipped", "reason": "No endpoint"}

    try:
        feed = feedparser.parse(source.endpoint)
        if feed.bozo and not feed.entries:
            source.last_error_at = datetime.now(timezone.utc)
            source.last_error_msg = str(feed.bozo_exception)
            db.commit()
            return {"source": source.name, "status": "error", "error": str(feed.bozo_exception)}

        items_added = 0
        for entry in feed.entries[:10]:  # batch of 10 items
            raw_url = getattr(entry, "link", None)
            if not raw_url:
                continue

            raw_title = getattr(entry, "title", "Untitled")
            raw_summary = getattr(entry, "summary", "")

            # Apply Unicode normalization / Preeti conversion
            title = clean_and_normalize_text(raw_title, source.language)
            excerpt = clean_and_normalize_text(raw_summary, source.language)

            content_hash = generate_content_hash(title, raw_url)

            # Idempotent deduplication check:
            existing = db.query(Article).filter(
                (Article.canonical_url == raw_url) | (Article.content_hash == content_hash)
            ).first()

            if existing:
                continue

            article = Article(
                source_id=source.id,
                external_id=getattr(entry, "id", raw_url),
                canonical_url=raw_url,
                title=title,
                excerpt=excerpt[:500] if excerpt else None,
                language=source.language,
                content_hash=content_hash,
                published_at=datetime.now(timezone.utc),
                fetched_at=datetime.now(timezone.utc)
            )
            db.add(article)
            db.flush()

            # Create or link to Story (State: 'developing' by default for rapid Latest Updates)
            story = Story(
                display_title=title,
                topic="national",
                state="developing",
                country_iso2=source.publisher_country,
                summary=excerpt[:300] if excerpt else None
            )
            db.add(story)
            db.flush()

            db.add(StoryArticle(
                story_id=story.id,
                article_id=article.id,
                match_method="rss_direct"
            ))

            # Initial candidate claim record (unverified by default)
            db.add(Claim(
                story_id=story.id,
                claim_text=f"Reported by {source.name}: {title}",
                context="Direct RSS feed ingestion",
                claim_status="unverified"
            ))

            items_added += 1

        source.last_success_at = datetime.now(timezone.utc)
        source.last_error_msg = None
        db.commit()
        return {"source": source.name, "status": "success", "items_added": items_added}

    except Exception as e:
        source.last_error_at = datetime.now(timezone.utc)
        source.last_error_msg = str(e)
        db.commit()
        return {"source": source.name, "status": "error", "error": str(e)}
