"""The core endpoint: a child reads aloud, the system returns an error profile.
When logged in, the result is saved to that student's history for the dashboard.
"""
import json
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from ..schemas import SessionResponse
from ..db import get_db
from ..models_db import ReadingSession, User
from ..auth import get_current_user_optional

router = APIRouter(prefix="/session", tags=["reading-session"])
_P: dict = {}


def _pipeline():
    if "pipe" not in _P:
        from ...inference.pipeline import ReadingSessionPipeline
        from ...inference.predictors import ErrorClassifierPredictor, RiskPredictor
        from ...models.m8_adaptive_coach import AdaptiveCoach
        from ...services.stt_service import STTService
        from ...common.config import load_config

        arms = load_config("configs/m8_bandit.yaml")["arms"]
        _P["pipe"] = ReadingSessionPipeline(
            error_clf=ErrorClassifierPredictor(),
            risk_scorer=RiskPredictor(),
            coach=AdaptiveCoach(arms),
            asr=STTService())
    return _P["pipe"]


@router.post("/analyze", response_model=SessionResponse)
async def analyze(audio: UploadFile = File(...),
                  target_text: str = Form(...),
                  child_id: str = Form("anon"),
                  db: Session = Depends(get_db),
                  user: User | None = Depends(get_current_user_optional)) -> SessionResponse:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        tmp.write(await audio.read())
        path = tmp.name
    result = _pipeline().run(path, target_text, utt_id=child_id)

    if user is not None:
        db.add(ReadingSession(
            user_id=user.id, target_text=target_text,
            wpm=result.wpm, accuracy=result.accuracy,
            risk_score=result.risk_score, risk_band=result.risk_band,
            next_exercise=result.next_exercise,
            error_rates_json=json.dumps(result.error_rates),
        ))
        db.commit()

    return SessionResponse(**{
        "utt_id": result.utt_id, "wpm": result.wpm, "accuracy": result.accuracy,
        "error_rates": result.error_rates, "word_errors": result.word_errors,
        "risk_score": result.risk_score, "risk_band": result.risk_band,
        "next_exercise": result.next_exercise})