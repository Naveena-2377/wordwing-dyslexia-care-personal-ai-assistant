from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
SYNTHETIC = DATA / "synthetic"
MODELS = ROOT / "models"
REPORTS = ROOT / "reports"
CONFIGS = ROOT / "configs"


def ensure(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
