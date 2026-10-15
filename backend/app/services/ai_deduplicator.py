import re
import math
from typing import Optional, Tuple, List, Set
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from ..models import Story, Article, StoryArticle, Claim, Evidence

# Common English and transliterated stop words
STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are",
    "was", "were", "been", "by", "with", "from", "as", "about", "into", "through",
    "after", "before", "over", "between", "out", "against", "during", "without",
    "reported", "breaking", "update", "wire", "special", "alert", "news", "reports",
    "shared", "confirmed", "today", "yesterday", "nepal", "nepali", "kathmandu"
}

def tokenize(text: str) -> List[str]:
    """Tokenize and clean words from text."""
    if not text:
        return []
    words = re.findall(r'[a-zA-Z0-9\u0900-\u097F]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]

def extract_named_entities(text: str) -> Set[str]:
    """
    Extracts key proper nouns, acronyms, locations, and key domain terms
    (e.g., 'nagdhunga', 'mustang', 'nrb', 'caan', 'nea', 'nepse', 'kirtipur', 'linge', 'ping').
    """
    tokens = set(tokenize(text))
    # Domain entities that carry high semantic weight in Nepal news context
    high_weight_entities = {
        "nagdhunga", "tunnel", "mustang", "manang", "mugling", "narayangadh",
        "dharan", "chitwan", "pokhara", "kirtipur", "bhaktapur", "patan",
        "nrb", "nea", "caan", "nepse", "neb", "kukl", "dotm", "fan", "nchl",
        "chyangra", "tika", "dakshina", "jamara", "phulpati", "marigold", "sayapatri",
        "gold", "tola", "jhapalish", "cricket", "rhinos", "5g", "paragliding"
    }
    return tokens.intersection(high_weight_entities)

def compute_cosine_similarity(vec1: dict, vec2: dict) -> float:
    """Computes cosine similarity between two word frequency vectors."""
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([val ** 2 for val in vec1.values()])
    sum2 = sum([val ** 2 for val in vec2.values()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    return float(numerator) / denominator

def calculate_semantic_similarity(title1: str, text1: str, title2: str, text2: str) -> float:
    """
    AI Semantic Similarity Matcher:
    Combines:
    1. Title token cosine similarity (weight: 0.40)
    2. Shared high-weight entity overlap (weight: 0.40)
    3. Body/summary text token overlap (weight: 0.20)
    Returns a score between 0.0 (unrelated) and 1.0 (identical/duplicate event).
    """
    tokens_title1 = tokenize(title1)
    tokens_title2 = tokenize(title2)
    
    if not tokens_title1 or not tokens_title2:
        return 0.0

    # Title word frequency vectors
    freq1 = {w: tokens_title1.count(w) for w in set(tokens_title1)}
    freq2 = {w: tokens_title2.count(w) for w in set(tokens_title2)}
    title_sim = compute_cosine_similarity(freq1, freq2)

    # High-weight entity intersection (locations, orgs, cultural keywords)
    ent1 = extract_named_entities(f"{title1} {text1}")
    ent2 = extract_named_entities(f"{title2} {text2}")
    
    if ent1 and ent2:
        shared_entities = ent1.intersection(ent2)
        entity_sim = len(shared_entities) / max(len(ent1), len(ent2))
    elif not ent1 and not ent2:
        entity_sim = title_sim
    else:
        entity_sim = 0.0

    # Summary text token overlap
    tokens_body1 = set(tokenize(text1))
    tokens_body2 = set(tokenize(text2))
    if tokens_body1 and tokens_body2:
        body_sim = len(tokens_body1.intersection(tokens_body2)) / max(len(tokens_body1), len(tokens_body2))
    else:
        body_sim = 0.0

    # Weighted overall semantic similarity
    combined_score = (title_sim * 0.45) + (entity_sim * 0.40) + (body_sim * 0.15)
    return round(combined_score, 4)

def find_matching_story(
    db: Session,
    incoming_title: str,
    incoming_summary: str,
    country_iso2: str = "NP",
    threshold: float = 0.55,
    within_hours: int = 48
) -> Optional[Tuple[Story, float]]:
    """
    Searches recent stories in the database within `within_hours`.
    Returns the matching existing Story and similarity score if score >= threshold,
    or None if this is a genuinely new story.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=within_hours)
    
    recent_stories = (
        db.query(Story)
        .filter(Story.country_iso2 == country_iso2, Story.first_seen_at >= cutoff)
        .order_by(Story.first_seen_at.desc())
        .all()
    )

    best_match: Optional[Story] = None
    best_score: float = 0.0

    for story in recent_stories:
        score = calculate_semantic_similarity(
            incoming_title,
            incoming_summary,
            story.display_title,
            story.summary or ""
        )
        if score > best_score:
            best_score = score
            best_match = story

    if best_score >= threshold:
        return best_match, best_score
    return None
