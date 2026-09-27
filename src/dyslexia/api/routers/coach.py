from fastapi import APIRouter

from ..schemas import CoachFeedback

router = APIRouter(prefix="/coach", tags=["adaptive-coach"])
_COACHES: dict = {}


def _get(child_id: str):
    from ...models.m8_adaptive_coach import AdaptiveCoach
    from ...common.config import load_config

    if child_id not in _COACHES:
        _COACHES[child_id] = AdaptiveCoach(load_config("configs/m8_bandit.yaml")["arms"])
    return _COACHES[child_id]


@router.get("/next/{child_id}")
def next_exercise(child_id: str) -> dict:
    return {"child_id": child_id, "exercise": _get(child_id).select()}


@router.post("/feedback")
def feedback(payload: CoachFeedback) -> dict:
    _get(payload.child_id).record(payload.exercise, payload.improved)
    return {"status": "recorded"}
