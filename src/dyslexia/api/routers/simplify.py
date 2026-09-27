from fastapi import APIRouter

from ..schemas import SimplifyRequest, SimplifyResponse
from ...services.readability import grade_level, passes

router = APIRouter(prefix="/simplify", tags=["simplify"])
_MODEL: dict = {}


def _load():
    if "model" not in _MODEL:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        from ...common.paths import MODELS

        path = str(MODELS / "m3_simplifier")
        _MODEL["tokenizer"] = AutoTokenizer.from_pretrained(path)
        _MODEL["model"] = AutoModelForSeq2SeqLM.from_pretrained(path)
    return _MODEL["tokenizer"], _MODEL["model"]


@router.post("", response_model=SimplifyResponse)
def simplify(req: SimplifyRequest) -> SimplifyResponse:
    tok, model = _load()
    inputs = tok("simplify: " + req.text, return_tensors="pt")
    out_ids = model.generate(**inputs, num_beams=4, max_new_tokens=80)
    candidate = tok.decode(out_ids[0], skip_special_tokens=True)
    source = "t5"
    if not passes(req.text, candidate, req.target_grade):
        candidate, source = req.text, "original"   # TODO: LLM fallback
    return SimplifyResponse(
        original=req.text, simplified=candidate,
        grade_level_before=grade_level(req.text),
        grade_level_after=grade_level(candidate), source=source)