"""Check a handwritten letter image for reversal (b/d, p/q, etc.) — powered by M1."""
import tempfile
import numpy as np
from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel

router = APIRouter(prefix="/handwriting", tags=["handwriting"])
_P: dict = {}
IMG = 64


def _preprocess(path: str) -> np.ndarray:
    import cv2
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("unreadable image")
    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = cv2.findNonZero(th)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
        th = th[y:y + h, x:x + w]
    h, w = th.shape
    size = max(h, w, 1)
    canvas = np.zeros((size, size), dtype=np.uint8)
    canvas[(size - h) // 2:(size - h) // 2 + h, (size - w) // 2:(size - w) // 2 + w] = th
    canvas = cv2.resize(canvas, (IMG, IMG), interpolation=cv2.INTER_AREA)
    return canvas.astype(np.float32) / 255.0


def _predictor():
    if "p" not in _P:
        from ...inference.predictors import HandwritingPredictor
        _P["p"] = HandwritingPredictor()
    return _P["p"]


class HandwritingResponse(BaseModel):
    normal: float
    reversal: float
    corrected: float
    verdict: str


@router.post("/check", response_model=HandwritingResponse)
async def check(image: UploadFile = File(...)) -> HandwritingResponse:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(await image.read())
        path = tmp.name
    arr = _preprocess(path)
    probs = _predictor().predict(arr)
    verdict = max(probs, key=probs.get)
    return HandwritingResponse(**probs, verdict=verdict)