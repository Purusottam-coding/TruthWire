from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(tags=["Health"])

@router.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "TruthWire API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pilot_countries": ["NP", "US", "CA"],
        "encoding": "UTF-8",
        "version": "1.0.0"
    }
