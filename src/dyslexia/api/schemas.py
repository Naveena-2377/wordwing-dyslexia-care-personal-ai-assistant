from pydantic import BaseModel, Field


class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=1)
    target_grade: int = 3


class SimplifyResponse(BaseModel):
    original: str
    simplified: str
    grade_level_before: float
    grade_level_after: float
    source: str          # "t5" | "llm" | "original"


class WordError(BaseModel):
    position: int
    target: str | None
    spoken: str | None
    label: str


class SessionResponse(BaseModel):
    utt_id: str
    wpm: float
    accuracy: float
    error_rates: dict[str, float]
    word_errors: list[WordError]
    risk_score: float
    risk_band: str
    next_exercise: str


class CoachFeedback(BaseModel):
    child_id: str
    exercise: str
    improved: bool


class SessionHistoryItem(BaseModel):
    id: int
    target_text: str
    wpm: float
    accuracy: float
    risk_score: float
    risk_band: str
    next_exercise: str
    created_at: str


class DashboardResponse(BaseModel):
    name: str
    total_sessions: int
    avg_wpm: float
    avg_accuracy: float
    latest_risk_band: str | None
    sessions: list[SessionHistoryItem]