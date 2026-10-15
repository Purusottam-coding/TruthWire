from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

class CountryBase(BaseModel):
    iso2: str
    name: str
    native_name: str
    flag_emoji: str
    enabled: bool = True

class CountryOut(CountryBase):
    id: str

    class Config:
        from_attributes = True

class SourceBase(BaseModel):
    name: str
    publisher_country: str
    source_type: str
    homepage_url: Optional[str] = None
    endpoint: Optional[str] = None
    language: str = "en"
    active: bool = True
    license_notes: Optional[str] = None
    credibility_rating: str = "standard_curated"

class SourceOut(SourceBase):
    id: str
    last_success_at: Optional[datetime] = None
    last_error_at: Optional[datetime] = None
    last_error_msg: Optional[str] = None

    class Config:
        from_attributes = True

class SourceCreate(SourceBase):
    pass

class ArticleOut(BaseModel):
    id: str
    source_id: str
    publisher_name: Optional[str] = None
    canonical_url: str
    title: str
    excerpt: Optional[str] = None
    full_content: Optional[str] = None
    image_url: Optional[str] = None
    language: str
    published_at: datetime
    fetched_at: datetime

    class Config:
        from_attributes = True

class EvidenceOut(BaseModel):
    id: str
    claim_id: str
    source_url: str
    source_name: str
    evidence_type: str
    stance: str
    excerpt: str
    independence_group: Optional[str] = None
    retrieved_at: datetime

    class Config:
        from_attributes = True

class EvidenceCreate(BaseModel):
    source_url: str
    source_name: str
    evidence_type: str
    stance: str
    excerpt: str
    independence_group: Optional[str] = None

class VerificationReviewOut(BaseModel):
    id: str
    claim_id: str
    reviewer_name: str
    decision: str
    rationale: str
    policy_version: str
    created_at: datetime

    class Config:
        from_attributes = True

class ReviewSubmission(BaseModel):
    reviewer_name: str
    decision: str  # promoted_to_verified, marked_corroborated, flagged_as_disputed, flagged_as_refuted, marked_inconclusive
    rationale: str
    policy_version: str = "v1.0"

class ClaimOut(BaseModel):
    id: str
    story_id: str
    claim_text: str
    context: Optional[str] = None
    claim_status: str
    extracted_at: datetime
    evidence_items: List[EvidenceOut] = []
    reviews: List[VerificationReviewOut] = []

    class Config:
        from_attributes = True

class AIAnalysisOut(BaseModel):
    credibility_score: int
    verdict: str  # LIKELY_AUTHENTIC, DEVELOPING_REPORT, SUSPICIOUS_UNVERIFIED
    verdict_label: str
    verdict_color: str  # emerald, amber, rose
    sensationalism_score: int
    attribution_score: int
    corroboration_sources_count: int
    signals: List[str] = []
    recommendation: str
    source_names: List[str] = []
    is_multi_source: bool = False

class StoryOut(BaseModel):
    id: str
    display_title: str
    topic: str
    state: str  # developing, under_review, verified_summary, corrected, retracted
    country_iso2: str
    first_seen_at: datetime
    updated_at: datetime
    summary: Optional[str] = None
    full_content: Optional[str] = None
    image_url: Optional[str] = None
    articles_count: int = 0
    claims_count: int = 0
    verified_claims_count: int = 0
    primary_source: Optional[str] = None
    articles: List[ArticleOut] = []
    claims: List[ClaimOut] = []
    ai_analysis: Optional[AIAnalysisOut] = None

    class Config:
        from_attributes = True

class AIScanRequest(BaseModel):
    text: str
    title: Optional[str] = None
    source_url: Optional[str] = None

class AIScanResponse(BaseModel):
    text: str
    credibility_score: int
    verdict: str
    verdict_label: str
    verdict_color: str
    sensationalism_score: int
    attribution_score: int
    signals: List[str]
    recommendation: str
    is_duplicate: bool
    duplicate_similarity_score: Optional[float] = None
    matched_story_id: Optional[str] = None
    matched_story_title: Optional[str] = None
    visited_sites: List[dict] = []
    actions_taken: List[str] = []

class StoryCorrection(BaseModel):
    actor: str
    reason: str
    new_state: str  # corrected, retracted, under_review
    new_summary: Optional[str] = None

class StatusHistoryOut(BaseModel):
    id: str
    entity_type: str
    entity_id: str
    old_status: str
    new_status: str
    actor: str
    reason: str
    changed_at: datetime

    class Config:
        from_attributes = True

class NewsFeedResponse(BaseModel):
    country: str
    feed: str  # latest or verified
    topic: Optional[str] = None
    total: int
    items: List[StoryOut]
