"""Upload a page -> OCR -> dyslexia-friendly text + synced audio."""
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/read", tags=["read-aloud"])


@router.post("/ocr")
async def ocr(file: UploadFile = File(...)) -> dict:
    from ..main import STATE

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name
    return STATE["ocr"].extract(path)


@router.post("/speak")
def speak(payload: dict) -> dict:
    from ..main import STATE

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    STATE["tts"].speak(payload["text"], out)
    return {"audio_path": out}


@router.post("/syllables")
def syllables(payload: dict) -> dict:
    from ..main import STATE

    return {"word": payload["word"],
            "syllables": STATE["tts"].syllabify(payload["word"])}
