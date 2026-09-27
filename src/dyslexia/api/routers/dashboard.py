"""Per-student dashboard: aggregate stats + session history for charts."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..schemas import DashboardResponse, SessionHistoryItem
from ..db import get_db
from ..models_db import User, ReadingSession
from ..auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/me", response_model=DashboardResponse)
def my_dashboard(user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)) -> DashboardResponse:
    sessions = (db.query(ReadingSession)
                .filter(ReadingSession.user_id == user.id)
                .order_by(ReadingSession.created_at.desc())
                .all())

    n = len(sessions)
    avg_wpm = sum(s.wpm for s in sessions) / n if n else 0.0
    avg_accuracy = sum(s.accuracy for s in sessions) / n if n else 0.0
    latest_band = sessions[0].risk_band if sessions else None

    return DashboardResponse(
        name=user.name,
        total_sessions=n,
        avg_wpm=avg_wpm,
        avg_accuracy=avg_accuracy,
        latest_risk_band=latest_band,
        sessions=[
            SessionHistoryItem(
                id=s.id, target_text=s.target_text, wpm=s.wpm,
                accuracy=s.accuracy, risk_score=s.risk_score,
                risk_band=s.risk_band, next_exercise=s.next_exercise,
                created_at=s.created_at.isoformat(),
            )
            for s in sessions
        ],
    )