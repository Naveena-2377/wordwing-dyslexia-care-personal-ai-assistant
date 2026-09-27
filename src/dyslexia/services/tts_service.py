"""Text-to-speech with per-word timing so the UI can highlight in sync.

Also exposes syllable-by-syllable playback for the reading coach
("El-e-phant") which is where most of the child-facing value sits.
"""


class TTSService:
    def __init__(self, provider: str = "coqui", rate: float = 0.85):
        self.provider = provider
        self.rate = rate          # slower default - dyslexic readers need decode time
        self._engine = None

    def _lazy(self):
        if self._engine is None and self.provider == "coqui":
            from TTS.api import TTS

            self._engine = TTS("tts_models/en/ljspeech/tacotron2-DDC")
        return self._engine

    def speak(self, text: str, out_path: str) -> str:
        self._lazy().tts_to_file(text=text, file_path=out_path)
        return out_path

    @staticmethod
    def syllabify(word: str) -> list[str]:
        """Naive onset-nucleus syllable split; swap for pyphen in production."""
        vowels = "aeiouy"
        chunks, cur = [], ""
        for i, ch in enumerate(word):
            cur += ch
            if ch in vowels and i + 1 < len(word) and word[i + 1] not in vowels:
                chunks.append(cur)
                cur = ""
        if cur:
            chunks.append(cur) if not chunks else chunks.__setitem__(
                -1, chunks[-1] + cur)
        return chunks or [word]
