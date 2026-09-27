"""Collect every module's metrics.json into one comparison table."""
import json

from ..common.paths import MODELS, REPORTS
from ..common.logging_utils import get_logger

log = get_logger(__name__)


def main() -> None:
    summary = {}
    for module_dir in sorted(MODELS.iterdir()):
        metrics = module_dir / "metrics.json"
        if metrics.exists():
            summary[module_dir.name] = json.loads(metrics.read_text(encoding="utf-8"))
    (REPORTS / "metrics" / "summary.json").parent.mkdir(parents=True, exist_ok=True)
    (REPORTS / "metrics" / "summary.json").write_text(json.dumps(summary, indent=2))
    log.info("collected metrics for %d modules", len(summary))


if __name__ == "__main__":
    main()
