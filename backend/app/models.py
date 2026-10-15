from datetime import datetime, timezone
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.orm import relationship
from .database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class Country(Base):
    __tablename__ = "countries"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    iso2 = Column(String(2), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    native_name = Column(String(100), nullable=False)
    flag_emoji = Column(String(10), nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)

    stories = relationship("Story", back_populates="country")
    sources = relationship("Source", back_populates="country")


class Source(Base):
    __tablename__ = "sources"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    publisher_country = Column(String(2), ForeignKey("countries.iso2"), nullable=False)
    source_type = Column(String(50), nullable=False)  # 'rss', 'licensed_api', 'official_api', 'approved_social', 'manual'
    homepage_url = Column(String(255), nullable=True)
    endpoint = Column(String(500), nullable=True)
    language = Column(String(10), default="en", nullable=False)  # 'ne', 'en'
    active = Column(Boolean, default=True, nullable=False)
    license_notes = Column(Text, nullable=True)
    credibility_rating = Column(String(50), default="standard_curated")  # e.g. official_gov, verified_outlet, community_wire
    last_success_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    last_error_msg = Column(Text, nullable=True)

    country = relationship("Country", back_populates="sources")
    articles = relationship("Article", back_populates="source")


class Article(Base):
    __tablename__ = "articles"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    source_id = Column(String(50), ForeignKey("sources.id"), nullable=False)
    external_id = Column(String(255), index=True, nullable=True)
    canonical_url = Column(String(1000), unique=True, index=True, nullable=False)
    title = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)
    language = Column(String(10), default="en", nullable=False)
    published_at = Column(DateTime, nullable=False, default=utc_now)
    fetched_at = Column(DateTime, nullable=False, default=utc_now)
    content_hash = Column(String(64), nullable=True)

    source = relationship("Source", back_populates="articles")
    story_associations = relationship("StoryArticle", back_populates="article")


class Story(Base):
    __tablename__ = "stories"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    display_title = Column(Text, nullable=False)
    topic = Column(String(50), index=True, default="national", nullable=False)
    # Story editorial state: developing, under_review, verified_summary, corrected, retracted
    state = Column(String(50), default="developing", index=True, nullable=False)
    country_iso2 = Column(String(2), ForeignKey("countries.iso2"), index=True, nullable=False)
    first_seen_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    summary = Column(Text, nullable=True)
    full_content = Column(Text, nullable=True)
    image_url = Column(String(1000), nullable=True)

    country = relationship("Country", back_populates="stories")
    articles = relationship("StoryArticle", back_populates="story", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="story", cascade="all, delete-orphan")


class StoryArticle(Base):
    __tablename__ = "story_articles"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    story_id = Column(String(50), ForeignKey("stories.id"), nullable=False)
    article_id = Column(String(50), ForeignKey("articles.id"), nullable=False)
    match_method = Column(String(50), default="canonical_cluster")
    match_confidence = Column(Float, default=1.0)

    story = relationship("Story", back_populates="articles")
    article = relationship("Article", back_populates="story_associations")


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    story_id = Column(String(50), ForeignKey("stories.id"), nullable=False)
    claim_text = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    # Claim assessment: unverified, checking, corroborated, disputed, refuted, inconclusive
    claim_status = Column(String(50), default="unverified", index=True, nullable=False)
    extracted_at = Column(DateTime, default=utc_now, nullable=False)

    story = relationship("Story", back_populates="claims")
    evidence_items = relationship("Evidence", back_populates="claim", cascade="all, delete-orphan")
    reviews = relationship("VerificationReview", back_populates="claim", cascade="all, delete-orphan")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False)
    source_url = Column(String(1000), nullable=False)
    source_name = Column(String(100), nullable=False)
    # Evidence type: primary_doc, official_statement, independent_reporting, fact_check
    evidence_type = Column(String(50), default="independent_reporting", nullable=False)
    # Stance: supports, refutes, contextual
    stance = Column(String(50), default="supports", nullable=False)
    excerpt = Column(Text, nullable=False)
    independence_group = Column(String(100), nullable=True)  # grouped by origin reporting chain
    retrieved_at = Column(DateTime, default=utc_now, nullable=False)

    claim = relationship("Claim", back_populates="evidence_items")


class VerificationReview(Base):
    __tablename__ = "verification_reviews"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    claim_id = Column(String(50), ForeignKey("claims.id"), nullable=False)
    reviewer_name = Column(String(100), nullable=False)
    # Decision: promoted_to_verified, marked_corroborated, flagged_as_disputed, flagged_as_refuted, marked_inconclusive
    decision = Column(String(50), nullable=False)
    rationale = Column(Text, nullable=False)
    policy_version = Column(String(20), default="v1.0", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    claim = relationship("Claim", back_populates="reviews")


class StatusHistory(Base):
    __tablename__ = "status_history"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    entity_type = Column(String(50), nullable=False)  # 'story' or 'claim'
    entity_id = Column(String(50), nullable=False)
    old_status = Column(String(50), nullable=False)
    new_status = Column(String(50), nullable=False)
    actor = Column(String(100), default="system", nullable=False)
    reason = Column(Text, nullable=False)
    changed_at = Column(DateTime, default=utc_now, nullable=False)
