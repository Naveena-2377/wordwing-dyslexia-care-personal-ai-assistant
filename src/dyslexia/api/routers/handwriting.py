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

def _segment_letters(path: str, min_area: int = 80, max_area_ratio: float = 0.04):
    import cv2
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("unreadable image")
    H, W = img.shape
    page_area = H * W

    _, th = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # remove long straight lines (ruled lines, page border) via morphological opening
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(25, W // 8), 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, max(25, H // 8)))
    lines = cv2.morphologyEx(th, cv2.MORPH_OPEN, h_kernel)
    lines = cv2.bitwise_or(lines, cv2.morphologyEx(th, cv2.MORPH_OPEN, v_kernel))
    th = cv2.subtract(th, lines)
    th = cv2.dilate(th, np.ones((2, 2), np.uint8), iterations=1)

    num, _, stats, _ = cv2.connectedComponentsWithStats(th, connectivity=8)
    boxes = []
    for i in range(1, num):
        x, y, w, h, area = stats[i]
        if area < min_area or area > page_area * max_area_ratio:
            continue
        if w < 5 or h < 8 or w > W * 0.25 or h > H * 0.25:
            continue
        if w / max(h, 1) > 4 or h / max(w, 1) > 4:
            continue
        boxes.append((x, y, w, h))
    if not boxes:
        return [], img

    avg_h = sum(b[3] for b in boxes) / len(boxes)
    boxes.sort(key=lambda b: b[1])
    out_lines, current, current_top = [], [boxes[0]], boxes[0][1]
    for b in boxes[1:]:
        if abs(b[1] - current_top) <= avg_h * 0.7:
            current.append(b)
        else:
            out_lines.append(current)
            current, current_top = [b], b[1]
    out_lines.append(current)
    return [b for line in out_lines for b in sorted(line, key=lambda bb: bb[0])], img


def _crop_to_64(img: np.ndarray, box) -> np.ndarray:
    import cv2
    x, y, w, h = box
    pad = max(2, int(0.15 * max(w, h)))
    y0, y1 = max(0, y - pad), min(img.shape[0], y + h + pad)
    x0, x1 = max(0, x - pad), min(img.shape[1], x + w + pad)
    crop = img[y0:y1, x0:x1]
    _, th = cv2.threshold(crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    size = max(th.shape)
    canvas = np.zeros((size, size), dtype=np.uint8)
    ch, cw = th.shape
    canvas[(size - ch)//2:(size - ch)//2 + ch, (size - cw)//2:(size - cw)//2 + cw] = th
    canvas = cv2.resize(canvas, (IMG, IMG), interpolation=cv2.INTER_AREA)
    return canvas.astype(np.float32) / 255.0


class LetterResult(BaseModel):
    index: int
    verdict: str
    reversal_prob: float
    bbox: list[int]


class PageCheckResponse(BaseModel):
    total_detected: int
    reversal_count: int
    reversal_rate: float
    image_width: int
    image_height: int
    letters: list[LetterResult]


@router.post("/check-page", response_model=PageCheckResponse)
async def check_page(image: UploadFile = File(...)) -> PageCheckResponse:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(await image.read())
        path = tmp.name

    boxes, img = _segment_letters(path)
    model = _predictor()
    results, reversal_count = [], 0
    for i, box in enumerate(boxes):
        crop = _crop_to_64(img, box)
        probs = model.predict(crop)
        verdict = max(probs, key=probs.get)
        if verdict == "reversal":
            reversal_count += 1
        results.append(LetterResult(
            index=i, verdict=verdict, reversal_prob=probs["reversal"],
            bbox=[int(box[0]), int(box[1]), int(box[2]), int(box[3])],
        ))

    total = len(results)
    h, w = img.shape
    return PageCheckResponse(
        total_detected=total, reversal_count=reversal_count,
        reversal_rate=(reversal_count / total) if total else 0.0,
        image_width=w, image_height=h,
        letters=results,
    )