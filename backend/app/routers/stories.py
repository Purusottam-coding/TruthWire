from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Story, Claim, StatusHistory
from ..schemas import StoryOut, ClaimOut, StatusHistoryOut, StoryCorrection
from .news import format_story_response

router = APIRouter(tags=["Stories & Fact Checking"])

@router.get("/stories/{story_id}", response_model=StoryOut)
def get_story_detail(story_id: str, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    return format_story_response(story)

@router.get("/stories/{story_id}/claims", response_model=List[ClaimOut])
def get_story_claims(story_id: str, db: Session = Depends(get_db)):
    story = db.query(Story).filter(Story.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    formatted = format_story_response(story)
    return formatted.claims

@router.get("/stories/{story_id}/history", response_model=List[StatusHistoryOut])
def get_story_history(story_id: str, db: Session = Depends(get_db)):
    history = db.query(StatusHistory).filter(
        StatusHistory.entity_type == "story",
        StatusHistory.entity_id == story_id
    ).order_by(StatusHistory.changed_at.desc()).all()
    return history
