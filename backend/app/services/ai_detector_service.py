import re
import math
from typing import Optional, Tuple, List, Set, Dict, Any
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from ..models import Story, Article, StoryArticle, Claim, Evidence, Source

# Stop words for English and Romanized Nepali
STOP_WORDS = {
    "a", "an", "the", "in", "on", "at", "for", "to", "of", "and", "or", "is", "are",
    "was", "were", "been", "by", "with", "from", "as", "about", "into", "through",
    "after", "before", "over", "between", "out", "against", "during", "without",
    "reported", "breaking", "update", "wire", "special", "alert", "news", "reports",
    "shared", "confirmed", "today", "yesterday", "nepal", "nepali", "kathmandu",
    "pani", "bata", "le", "ko", "maa", "haru", "cha", "thiyo", "ra", "bhanera"
}

# High-weight named entities and domain tokens in Nepal's news context
DOMAIN_ENTITIES = {
    "nagdhunga", "tunnel", "mustang", "manang", "mugling", "narayangadh",
    "dharan", "chitwan", "pokhara", "kirtipur", "bhaktapur", "patan", "gorkha", "humla",
    "nrb", "nea", "caan", "nepse", "neb", "kukl", "dotm", "fan", "nchl", "can",
    "police", "court", "parliament", "ministry", "minister", "gold", "tola",
    "cricket", "rhinos", "npl", "spikenard", "dolpa", "malaysia", "foreign"
}

# Sensationalist, clickbait, and rumor indicators
SENSATIONAL_PATTERNS = [
    r"\b(shocking|unbelievable|omg|must watch|viral leaked|exposed|dhamaaka|tabahi)\b",
    r"\b(secret revealed|kanda|halka ramailo|you won\'t believe|hidden truth)\b",
    r"\b(panicked|disaster imminent|banned forever|urgent share)\b",
    r"(!{2,}|\?{2,})",  # Multiple exclamation or question marks
    r"\b[A-Z]{4,}\b",     # ALL CAPS words (e.g. SHOCKING, BREAKING)
]

# Verified institutional authority keywords
INSTITUTIONAL_KEYWORDS = [
    "nepal police", "district traffic police", "supreme court", "high court",
    "nepal rastra bank", "nrb", "department of roads", "civil aviation", "caan",
    "nepal electricity authority", "nea", "ministry of finance", "ministry of home",
    "hazama ando", "armed police force", "apf", "cricket association of nepal", "can",
    "spokesperson", "director general", "press release", "official gazette", "statement confirmed"
]

def tokenize(text: str) -> List[str]:
    """Tokenizes text into clean words."""
    if not text:
        return []
    words = re.findall(r'[a-zA-Z0-9\u0900-\u097F]+', text.lower())
    return [w for w in words if len(w) > 2 and w not in STOP_WORDS]

def extract_named_entities(text: str) -> Set[str]:
    """Extracts named domain entities from text."""
    tokens = set(tokenize(text))
    return tokens.intersection(DOMAIN_ENTITIES)

def compute_cosine_similarity(vec1: dict, vec2: dict) -> float:
    """Computes cosine similarity between two frequency vectors."""
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
    Computes overall semantic similarity between two news stories.
    Returns 0.0 (completely distinct) to 1.0 (exact duplicate event).
    """
    tokens_title1 = tokenize(title1)
    tokens_title2 = tokenize(title2)
    if not tokens_title1 or not tokens_title2:
        return 0.0

    freq1 = {w: tokens_title1.count(w) for w in set(tokens_title1)}
    freq2 = {w: tokens_title2.count(w) for w in set(tokens_title2)}
    title_sim = compute_cosine_similarity(freq1, freq2)

    ent1 = extract_named_entities(f"{title1} {text1}")
    ent2 = extract_named_entities(f"{title2} {text2}")
    if ent1 and ent2:
        shared = ent1.intersection(ent2)
        entity_sim = len(shared) / max(len(ent1), len(ent2))
    elif not ent1 and not ent2:
        entity_sim = title_sim
    else:
        entity_sim = 0.0

    tokens_body1 = set(tokenize(text1))
    tokens_body2 = set(tokenize(text2))
    if tokens_body1 and tokens_body2:
        body_sim = len(tokens_body1.intersection(tokens_body2)) / max(len(tokens_body1), len(tokens_body2))
    else:
        body_sim = 0.0

    combined = (title_sim * 0.45) + (entity_sim * 0.40) + (body_sim * 0.15)
    return round(combined, 4)

def find_matching_story(
    db: Session,
    incoming_title: str,
    incoming_summary: str,
    country_iso2: str = "NP",
    threshold: float = 0.52,
    within_hours: int = 48
) -> Optional[Tuple[Story, float]]:
    """
    Searches active stories within the 48-hour window.
    Returns (matching_story, similarity_score) if score >= threshold, else None.
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

    if best_score >= threshold and best_match is not None:
        return best_match, best_score
    return None

def analyze_fake_news_and_credibility(
    title: str,
    content: str,
    source_name: Optional[str] = None,
    articles_count: int = 1,
    corroborating_sources: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    AI Fake News, Rumor & Credibility Detector Engine.
    Evaluates:
    - Sensationalism & clickbait indicators
    - Institutional authority citations
    - Cross-source multi-outlet corroboration
    - Generates credibility score (0-100), verdict, and explainable signals.
    """
    combined_text = f"{title} {content}".lower()
    signals: List[str] = []
    
    # 1. Sensationalism Score (0 = Clean Journalistic, 100 = Severe Clickbait/Rumor)
    sensational_hits = 0
    for pattern in SENSATIONAL_PATTERNS:
        matches = re.findall(pattern, f"{title} {content}", re.IGNORECASE)
        sensational_hits += len(matches)

    sensationalism_score = min(100, sensational_hits * 25)

    if sensationalism_score > 40:
        signals.append("⚠️ Elevated sensationalism or hyperbolic language detected in text.")
    else:
        signals.append("✓ Factual, neutral journalistic tone without clickbait markers.")

    # 2. Institutional Attribution Score (0 = Anonymous/Vague, 100 = Explicit Official Bodies)
    inst_hits = 0
    cited_institutions = []
    for inst in INSTITUTIONAL_KEYWORDS:
        if inst in combined_text:
            inst_hits += 1
            cited_institutions.append(inst.title())

    if inst_hits > 0:
        attribution_score = min(100, 60 + (inst_hits * 15))
        unique_insts = list(dict.fromkeys(cited_institutions))[:3]
        signals.append(f"✓ Cites authentic institutional sources: {', '.join(unique_insts)}.")
    else:
        attribution_score = 45
        signals.append("ℹ️ Preliminary wire report without direct official spokesperson quotes.")

    # 3. Source Credibility Baseline
    src_clean = (source_name or "").lower()
    if any(k in src_clean for k in ["onlinekhabar", "setopati", "kathmandu post", "rss", "kantipur"]):
        source_base_score = 90
        signals.append("✓ Originates from an accredited national news organization.")
    elif "routine of nepal" in src_clean or "ronb" in src_clean:
        source_base_score = 82
        signals.append("✓ Sourced from Routine of Nepal Banda (RONB) verified social wire.")
    elif any(k in src_clean for k in ["nrb", "army", "caan", "police", "nea"]):
        source_base_score = 98
        signals.append("✓ Direct gazette report from an official constitutional/statutory authority.")
    else:
        source_base_score = 65

    # 4. Multi-Source Corroboration Boost
    corrob_count = articles_count
    if corroborating_sources:
        corrob_count = max(corrob_count, len(corroborating_sources))

    corroboration_score = 50
    if corrob_count >= 2:
        corroboration_score = 95
        sources_str = ", ".join(corroborating_sources[:2]) if corroborating_sources else "multiple outlets"
        signals.append(f"✓ Cross-corroborated by independent news outlets ({sources_str}).")
    else:
        signals.append("ℹ️ Single-source dispatch; monitoring national wire for corroboration.")

    # 5. Composite Authenticity Calculation
    # Weights: Source Baseline (30%), Attribution (25%), Corroboration (30%), Inverse Sensationalism (15%)
    weighted_score = (
        (source_base_score * 0.30) +
        (attribution_score * 0.25) +
        (corroboration_score * 0.30) +
        ((100 - sensationalism_score) * 0.15)
    )
    final_score = int(round(max(5, min(99, weighted_score))))

    # 6. Verdict Classification
    if final_score >= 82:
        verdict = "LIKELY_AUTHENTIC"
        verdict_label = "Authentic & Verified"
        verdict_color = "emerald"
        recommendation = "Safe to share. Factual reporting supported by verifiable context."
    elif final_score >= 60:
        verdict = "DEVELOPING_REPORT"
        verdict_label = "Developing Wire"
        verdict_color = "amber"
        recommendation = "Developing story with credible origin. Watch for corroborating statements."
    else:
        verdict = "SUSPICIOUS_UNVERIFIED"
        verdict_label = "Unverified / Caution"
        verdict_color = "rose"
        recommendation = "Caution advised: Unverified claims or sensational tone detected."

    return {
        "credibility_score": final_score,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_color": verdict_color,
        "sensationalism_score": sensationalism_score,
        "attribution_score": attribution_score,
        "corroboration_sources_count": corrob_count,
        "signals": signals,
        "recommendation": recommendation,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }


import urllib.request
import ssl
import xml.etree.ElementTree as ET

def verify_claim_against_live_websites(
    query_text: str,
    db: Session,
    threshold: float = 0.40
) -> Dict[str, Any]:
    """
    Actively visits top authentic Nepali news websites (OnlineKhabar English, Setopati,
    The Kathmandu Post, and national wire) to verify whether a claim/news is authentic or a rumor.
    If authentic reports are found, automatically updates/promotes the news in the database.
    """
    clean_query = query_text.strip()
    visited_sites = []
    matched_articles = []
    ssl_ctx = ssl._create_unverified_context()

    # 1. Visit OnlineKhabar English Live Feed
    try:
        ok_url = "https://english.onlinekhabar.com/feed"
        req = urllib.request.Request(ok_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=6) as res:
            xml_data = res.read()
        tree = ET.fromstring(xml_data)
        ok_items = tree.findall(".//item")
        ok_match = None
        ok_best_score = 0.0

        for item in ok_items:
            title = (item.find("title").text or "").strip()
            desc = (item.find("description").text or "").strip()
            link = (item.find("link").text or "").strip()
            score = calculate_semantic_similarity(clean_query, clean_query, title, desc)
            if score > ok_best_score:
                ok_best_score = score
                if score >= threshold:
                    ok_match = {"title": title, "url": link, "score": score, "source": "OnlineKhabar English"}

        if ok_match:
            visited_sites.append({"name": "OnlineKhabar English", "url": ok_match["url"], "status": "VERIFIED_MATCH", "match_score": round(ok_best_score * 100, 1), "article_title": ok_match["title"]})
            matched_articles.append(ok_match)
        else:
            visited_sites.append({"name": "OnlineKhabar English", "url": "https://english.onlinekhabar.com", "status": "NO_MATCH", "match_score": round(ok_best_score * 100, 1)})
    except Exception as e:
        visited_sites.append({"name": "OnlineKhabar English", "url": "https://english.onlinekhabar.com", "status": "VISIT_TIMEOUT", "error": str(e)[:60]})

    # 2. Visit Setopati
    try:
        sp_url = "https://www.setopati.com/"
        req = urllib.request.Request(sp_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=6) as res:
            html = res.read().decode('utf-8', errors='ignore')
        
        # Extract titles from headline links in Setopati HTML
        sp_titles = re.findall(r'<a[^>]+href=["\'](https://(?:www\.)?setopati\.com/[^"\']+)["\'][^>]*>([^<]+)</a>', html)
        sp_match = None
        sp_best_score = 0.0

        for link, title_raw in sp_titles:
            title = title_raw.strip()
            if len(title) < 15:
                continue
            score = calculate_semantic_similarity(clean_query, clean_query, title, title)
            if score > sp_best_score:
                sp_best_score = score
                if score >= threshold:
                    sp_match = {"title": title, "url": link, "score": score, "source": "Setopati"}

        if sp_match:
            visited_sites.append({"name": "Setopati", "url": sp_match["url"], "status": "VERIFIED_MATCH", "match_score": round(sp_best_score * 100, 1), "article_title": sp_match["title"]})
            matched_articles.append(sp_match)
        else:
            visited_sites.append({"name": "Setopati", "url": "https://www.setopati.com", "status": "NO_MATCH", "match_score": round(sp_best_score * 100, 1)})
    except Exception as e:
        visited_sites.append({"name": "Setopati", "url": "https://www.setopati.com", "status": "VISIT_TIMEOUT", "error": str(e)[:60]})

    # 3. Visit The Kathmandu Post
    try:
        tkp_url = "https://kathmandupost.com/"
        req = urllib.request.Request(tkp_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, context=ssl_ctx, timeout=6) as res:
            html = res.read().decode('utf-8', errors='ignore')

        tkp_matches = re.findall(r'<a[^>]+href=["\'](/[^"\']+|https://kathmandupost\.com/[^"\']+)["\'][^>]*>([^<]+)</a>', html)
        tkp_match = None
        tkp_best_score = 0.0

        for link_rel, title_raw in tkp_matches:
            title = title_raw.strip()
            if len(title) < 20:
                continue
            score = calculate_semantic_similarity(clean_query, clean_query, title, title)
            if score > tkp_best_score:
                tkp_best_score = score
                if score >= threshold:
                    full_link = link_rel if link_rel.startswith("http") else f"https://kathmandupost.com{link_rel}"
                    tkp_match = {"title": title, "url": full_link, "score": score, "source": "The Kathmandu Post"}

        if tkp_match:
            visited_sites.append({"name": "The Kathmandu Post", "url": tkp_match["url"], "status": "VERIFIED_MATCH", "match_score": round(tkp_best_score * 100, 1), "article_title": tkp_match["title"]})
            matched_articles.append(tkp_match)
        else:
            visited_sites.append({"name": "The Kathmandu Post", "url": "https://kathmandupost.com", "status": "NO_MATCH", "match_score": round(tkp_best_score * 100, 1)})
    except Exception as e:
        visited_sites.append({"name": "The Kathmandu Post", "url": "https://kathmandupost.com", "status": "VISIT_TIMEOUT", "error": str(e)[:60]})

    # 4. Check Internal TruthWire Database & Update Stories
    db_match = find_matching_story(db, clean_query, clean_query, country_iso2="NP", threshold=0.45)
    matched_db_story = None
    if db_match:
        matched_db_story, db_sim = db_match
        primary_src = matched_db_story.articles[0].article.source.name if matched_db_story.articles and matched_db_story.articles[0].article and matched_db_story.articles[0].article.source else "TruthWire Wire"
        visited_sites.append({"name": "TruthWire National Wire", "url": matched_db_story.articles[0].article.canonical_url if matched_db_story.articles and matched_db_story.articles[0].article else "https://truthwire.np", "status": "VERIFIED_MATCH", "match_score": round(db_sim * 100, 1), "article_title": matched_db_story.display_title})
        matched_articles.append({"title": matched_db_story.display_title, "url": matched_db_story.articles[0].article.canonical_url if matched_db_story.articles and matched_db_story.articles[0].article else "", "score": db_sim, "source": primary_src})

    # 5. Update News in Database based on Live Website Visits
    action_log = []
    now = datetime.now(timezone.utc)

    if matched_articles:
        # Authentic reports found on visited websites!
        if matched_db_story:
            # Promote developing story to verified_summary because live website confirmed it!
            if matched_db_story.state != "verified_summary":
                matched_db_story.state = "verified_summary"
                action_log.append("Promoted developing story to 'Verified Summary' based on live website confirmation.")

            matched_db_story.updated_at = now
            # Attach live evidence if new outlet found
            for m in matched_articles:
                if matched_db_story.claims and m.get("url"):
                    existing_ev = db.query(Evidence).filter(Evidence.source_url == m["url"]).first()
                    if not existing_ev:
                        db.add(Evidence(
                            claim_id=matched_db_story.claims[0].id,
                            source_url=m["url"],
                            source_name=m["source"],
                            evidence_type="news_report",
                            stance="supports",
                            excerpt=f"Live website verification confirmed story on {m['source']}: {m['title']}",
                            independence_group=m["source"].upper()
                        ))
                        action_log.append(f"Attached live corroborating evidence link from {m['source']}.")
            db.commit()
        else:
            # Ingest new verified story from the live visited match
            top_m = matched_articles[0]
            new_story = Story(
                display_title=top_m["title"],
                topic="national",
                state="verified_summary",
                country_iso2="NP",
                first_seen_at=now,
                updated_at=now,
                summary=f"Verified live report from {top_m['source']}: {top_m['title']}",
                full_content=f"Reported and verified directly via live visit to {top_m['source']} ({top_m.get('url', '')}).",
                image_url="https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?auto=format&fit=crop&w=1200&q=80"
            )
            db.add(new_story)
            db.flush()

            # Find or create source
            src = db.query(Source).filter(Source.name.ilike(f"%{top_m['source'][:10]}%")).first()
            if not src:
                src = Source(
                    name=top_m["source"],
                    publisher_country="NP",
                    source_type="rss",
                    homepage_url=top_m.get("url", "https://truthwire.np"),
                    language="en",
                    active=True,
                    credibility_rating="verified_outlet"
                )
                db.add(src)
                db.flush()

            art = Article(
                source_id=src.id,
                canonical_url=top_m.get("url", f"https://truthwire.np/story/{new_story.id}"),
                title=top_m["title"],
                excerpt=new_story.summary,
                full_content=new_story.full_content,
                image_url=new_story.image_url,
                language="en",
                published_at=now,
                fetched_at=now
            )
            db.add(art)
            db.flush()
            db.add(StoryArticle(story_id=new_story.id, article_id=art.id))

            cl = Claim(
                story_id=new_story.id,
                claim_text=top_m["title"],
                context=f"Verified via live website visit to {top_m['source']}",
                claim_status="corroborated",
                extracted_at=now
            )
            db.add(cl)
            db.flush()

            db.add(Evidence(
                claim_id=cl.id,
                source_url=top_m.get("url", "https://truthwire.np"),
                source_name=top_m["source"],
                evidence_type="news_report",
                stance="supports",
                excerpt=f"Confirmed and verified from live website: {top_m['title']}",
                independence_group=top_m["source"].upper()
            ))
            db.commit()
            action_log.append(f"Ingested fresh verified story directly from live {top_m['source']} website visit into database.")

    # 6. Synthesize Live Verdict
    is_verified_live = len(matched_articles) > 0
    if is_verified_live:
        verdict = "AUTHENTIC_VERIFIED"
        verdict_label = "Authentic & Verified on Live Websites"
        verdict_color = "emerald"
        recommendation = f"Verified: Found matching reporting on {len(matched_articles)} authentic news portal(s). Database updated."
    else:
        # Check if sensationalism indicates a rumor
        sensational_hits = sum(len(re.findall(pat, clean_query, re.IGNORECASE)) for pat in SENSATIONAL_PATTERNS)
        if sensational_hits > 0 or len(clean_query.split()) > 4:
            verdict = "UNVERIFIED_RUMOR"
            verdict_label = "Unconfirmed Rumor (0 Outlets Found)"
            verdict_color = "rose"
            recommendation = "Live website visit complete: 0 authentic news portals reported this. Classified as an unverified rumor."
        else:
            verdict = "NO_LIVE_COVERAGE"
            verdict_label = "No Coverage Found"
            verdict_color = "zinc"
            recommendation = "No current reporting found across OnlineKhabar, Setopati, or Kathmandu Post for this specific query."

    return {
        "query": clean_query,
        "is_verified_on_web": is_verified_live,
        "verdict": verdict,
        "verdict_label": verdict_label,
        "verdict_color": verdict_color,
        "matched_articles_count": len(matched_articles),
        "matched_articles": matched_articles,
        "visited_sites": visited_sites,
        "actions_taken": action_log,
        "recommendation": recommendation,
        "timestamp": now.isoformat()
    }
