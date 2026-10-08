"""Generate a personalized reading-comprehension quiz from an uploaded document."""
import tempfile
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/quiz", tags=["quiz"])


class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_index: int
    explanation: str


class QuizResponse(BaseModel):
    title: str
    questions: list[QuizQuestion]


def _extract_pdf_text(path: str) -> str:
    from pypdf import PdfReader
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(file: UploadFile = File(...), num_questions: int = Form(5)) -> QuizResponse:
    suffix = ("." + file.filename.rsplit(".", 1)[-1].lower()) if "." in file.filename else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    if suffix == ".pdf":
        text = _extract_pdf_text(path)
    elif suffix == ".txt":
        text = open(path, encoding="utf-8", errors="ignore").read()
    else:
        from ..main import STATE
        text = STATE["ocr"].extract(path)["text"]

    text = text.strip()
    if not text:
        raise HTTPException(400, "Couldn't read any text from that file.")

    from ...services.llm_service import LLMService
    quiz = LLMService().generate_quiz(text, num_questions)
    return QuizResponse(**quiz)