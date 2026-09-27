"""Concept -> illustration for the visual learning generator.

Cache aggressively: the same 200 curriculum concepts repeat across every child,
and generation is the slowest and most expensive call in the whole system.
"""
import hashlib
from pathlib import Path


class ImageGenService:
    def __init__(self, provider: str = "stable_diffusion_api",
                 cache_dir: str = "data/external/concept_images"):
        self.provider = provider
        self.cache = Path(cache_dir)
        self.cache.mkdir(parents=True, exist_ok=True)

    def _key(self, concept: str) -> Path:
        return self.cache / f"{hashlib.sha1(concept.lower().encode()).hexdigest()}.png"

    def generate(self, concept: str) -> Path:
        path = self._key(concept)
        if path.exists():
            return path
        raise NotImplementedError("Wire your image API here, then save to `path`.")
