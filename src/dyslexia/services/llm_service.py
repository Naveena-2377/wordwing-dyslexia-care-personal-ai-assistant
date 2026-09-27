"""LLM fallback for simplification + child-friendly Q&A.

The fine-tuned T5 is the primary simplifier; the LLM covers open-ended questions
and sentences where the local model's output fails the readability check.
"""
import os


SYSTEM_PROMPT = (
    "You explain things to a 7-9 year old child with dyslexia. "
    "Use short sentences of at most 12 words. Use common words. "
    "One idea per sentence. Never use metaphor that needs background knowledge."
)


class LLMService:
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.api_key = os.getenv(f"{provider.upper()}_API_KEY", "")

    def answer(self, question: str, context: str = "") -> str:
        raise NotImplementedError(
            "Wire your provider SDK here. Keep SYSTEM_PROMPT unchanged - "
            "the readability guarantee depends on it."
        )

    def simplify(self, sentence: str) -> str:
        raise NotImplementedError
