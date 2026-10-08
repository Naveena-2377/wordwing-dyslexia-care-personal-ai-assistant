"""Sentence simplification: Gemini primary, T5 fallback, original as last resort."""
from fastapi import APIRouter

from ..schemas import SimplifyRequest, SimplifyResponse
from ...services.readability import grade_level, passes
from ...services.llm_service import LLMService
from ...common.logging_utils import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/simplify", tags=["simplify"])
_MODEL: dict = {}
_llm = LLMService()


def _load_t5():
    if "model" not in _MODEL:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        from ...common.paths import MODELS
        path = str(MODELS / "m3_simplifier")
        _MODEL["tokenizer"] = AutoTokenizer.from_pretrained(path)
        _MODEL["model"] = AutoModelForSeq2SeqLM.from_pretrained(path)
    return _MODEL["tokenizer"], _MODEL["model"]


def _simplify_t5(text: str) -> str:
    tok, model = _load_t5()
    inputs = tok("simplify: " + text, return_tensors="pt")
    out_ids = model.generate(**inputs, num_beams=4, max_new_tokens=80)
    return tok.decode(out_ids[0], skip_special_tokens=True)


@router.post("", response_model=SimplifyResponse)
def simplify(req: SimplifyRequest) -> SimplifyResponse:
    candidate, source = req.text, "original"

    try:
        gemini_out = _llm.simplify(req.text)
        log.info("gemini output: %s", gemini_out)
        if passes(req.text, gemini_out, req.target_grade):
            candidate, source = gemini_out, "gemini"
        else:
            log.info("gemini output failed readability check")
    except Exception as exc:
        log.error("gemini simplify failed: %s", exc)

    if source == "original":
        try:
            t5_out = _simplify_t5(req.text)
            if passes(req.text, t5_out, req.target_grade):
                candidate, source = t5_out, "t5"
        except Exception as exc:
            log.error("t5 simplify failed: %s", exc)

    return SimplifyResponse(
        original=req.text, simplified=candidate,
        grade_level_before=grade_level(req.text),
        grade_level_after=grade_level(candidate), source=source)