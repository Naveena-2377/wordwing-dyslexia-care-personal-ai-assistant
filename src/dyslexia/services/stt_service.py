"""Speech-to-text with word timestamps (Whisper)."""


class STTService:
    def __init__(self, model_size: str = "small", language: str = "en"):
        self.model_size = model_size
        self.language = language
        self._model = None

    def _lazy(self):
        if self._model is None:
            import whisper

            self._model = whisper.load_model(self.model_size)
        return self._model

    def transcribe(self, audio_path: str) -> dict:
        result = self._lazy().transcribe(audio_path, word_timestamps=True,
                                         language=self.language)
        words = [{"word": w["word"].strip(), "start": w["start"], "end": w["end"],
                  "prob": w.get("probability", 1.0)}
                 for seg in result["segments"] for w in seg.get("words", [])]
        return {"text": result["text"], "words": words}
