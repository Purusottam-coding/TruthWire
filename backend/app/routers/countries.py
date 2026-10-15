from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Country
from ..schemas import CountryOut

router = APIRouter(tags=["Countries & Topics"])

@router.get("/countries", response_model=List[CountryOut])
def list_countries(db: Session = Depends(get_db)):
    """Returns enabled countries (NP, US, CA and worldwide additions)."""
    return db.query(Country).filter(Country.enabled == True).all()

@router.get("/topics")
def list_topics():
    """Returns standardized news topics with English and Nepali localization."""
    return [
        {"id": "all", "name_en": "All Topics", "name_ne": "सबै विषय"},
        {"id": "national", "name_en": "National", "name_ne": "राष्ट्रिय"},
        {"id": "politics", "name_en": "Politics", "name_ne": "राजनीति"},
        {"id": "business", "name_en": "Business & Economy", "name_ne": "अर्थतन्त्र र व्यापार"},
        {"id": "technology", "name_en": "Technology", "name_ne": "प्रविधि"},
        {"id": "weather", "name_en": "Weather & Climate", "name_ne": "मौसम तथा वातावरण"},
        {"id": "sports", "name_en": "Sports", "name_ne": "खेलकुद"},
    ]
