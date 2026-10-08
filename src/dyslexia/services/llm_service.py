"""Gemini-backed sentence simplification and quiz generation.

Free-tier Gemini can return 503 under load, so:
  - several models are tried in order, and the whole chain is tried twice
  - every successful result is cached on disk, so inputs you've run once
    keep working even if Google is down
"""
import hashlib
import json
import os
import re
import time

import requests

from ..common.paths import DATA

SYSTEM_PROMPT = (
    "You rewrite sentences for a child with dyslexia, ages 7-10. "
    "Rules: use short sentences (max 12 words each). Use simple, common words. "
    "Keep the original meaning exactly. One idea per sentence. "
    "Output ONLY the rewritten text - no preamble, no explanation."
)

MODELS = ["gemini-3.5-flash", "gemini-3.8-flash"]
CACHE_PATH = DATA / "external" / "llm_cache.json"


def _cache_key(kind: str, *parts) -> str:
    raw = kind + "|" + "|".join(str(p) for p in parts)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _cache_load() -> dict:
    try:
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _cache_save(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")


class LLMService:
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        self.api_key = os.getenv("GEMINI_API_KEY", "")

    def _generate(self, prompt: str, max_tokens: int, timeout: int) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.3, "maxOutputTokens": max_tokens},
        }
        headers = {"x-goog-api-key": self.api_key}
        last_error = None
        for round_no in range(2):
            for model in MODELS:
                url = ("https://generativelanguage.googleapis.com/v1beta/models/"
                       f"{model}:generateContent")
                try:
                    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
                    resp.raise_for_status()
                    candidate = resp.json()["candidates"][0]
                    if candidate.get("finishReason") == "MAX_TOKENS":
                        last_error = RuntimeError(f"{model}: response truncated")
                        continue
                    parts = candidate.get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts).strip()
                    if text:
                        return text
                    last_error = RuntimeError(f"{model}: empty response")
                except Exception as exc:
                    last_error = exc
            if round_no == 0:
                time.sleep(2)
        raise last_error

    def simplify(self, sentence: str) -> str:
        key = _cache_key("simplify", sentence.strip())
        cache = _cache_load()
        if key in cache:
            return cache[key]
        text = self._generate(f"{SYSTEM_PROMPT}\n\nSentence: {sentence}", 1024, 15)
        cache[key] = text
        _cache_save(cache)
        return text

    def generate_quiz(self, text: str, num_questions: int = 5) -> dict:
        snippet = text[:1500]
        key = _cache_key("quiz", num_questions, snippet)
        cache = _cache_load()
        if key in cache:
            return cache[key]

        prompt = (
            f"Create exactly {num_questions} simple multiple-choice reading-comprehension "
            "questions for a child aged 7-10 with dyslexia, based on this text. "
            "Use short, simple words. Each question needs exactly 4 options, "
            "one correct_index (0-3), and a one-sentence kid-friendly explanation. "
            "Respond with ONLY a JSON object, no markdown fences, no extra text. Format:\n"
            '{"title": "...", "questions": [{"question": "...", '
            '"options": ["...","...","...","..."], "correct_index": 0, "explanation": "..."}]}\n\n'
            f"Text:\n{snippet}"
        )
        quiz, last_error = None, None
        for _ in range(2):
            raw = self._generate(prompt, 2048, 60)
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
            try:
                quiz = json.loads(raw)
                break
            except json.JSONDecodeError as exc:
                last_error = exc
        if quiz is None:
            raise last_error
        cache[key] = quiz
        _cache_save(cache)
        return quiz