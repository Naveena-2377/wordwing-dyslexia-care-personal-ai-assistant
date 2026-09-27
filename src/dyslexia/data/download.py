"""Dataset registry + download helper.

Kaggle datasets need the Kaggle CLI and a kaggle.json token.
Zenodo/HuggingFace are direct.
"""
import subprocess
from ..common.paths import RAW
from ..common.logging_utils import get_logger

log = get_logger(__name__)

REGISTRY = {
    "m1_dyslexia_handwriting": {
        "source": "kaggle",
        "id": "drizasazanitaisa/dyslexia-handwriting-dataset",
        "dest": RAW / "m1_dyslexia_handwriting",
    },
    "m1_synthetic_yolo": {
        "source": "kaggle",
        "id": "michaelfink0923/synthetic-dyslexia-handwriting-dataset",
        "dest": RAW / "m1_synthetic_yolo",
    },
    "m1_emnist": {
        "source": "kaggle",
        "id": "crawford/emnist",
        "dest": RAW / "m1_emnist",
    },
    "m2_nnces": {
        "source": "kaggle",
        "id": "kodaliradha20phd7093/nonnative-children-english-speech-nnces-corpus",
        "dest": RAW / "m2_nnces",
    },
    "m2_children_speech": {
        "source": "zenodo",
        "id": "200495",
        "dest": RAW / "m2_children_speech",
    },
    "m3_wikilarge": {
        "source": "huggingface",
        "id": "waboucay/wikilarge",
        "dest": RAW / "m3_wikilarge",
    },
    "m6_etdd70": {
        "source": "zenodo",
        "id": "13332134",
        "dest": RAW / "m6_etdd70",
    },
}


def download(key: str) -> None:
    spec = REGISTRY[key]
    spec["dest"].mkdir(parents=True, exist_ok=True)
    log.info("Downloading %s from %s", key, spec["source"])
    if spec["source"] == "kaggle":
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", spec["id"],
             "-p", str(spec["dest"]), "--unzip"],
            check=True,
        )
    elif spec["source"] == "huggingface":
        from datasets import load_dataset

        load_dataset(spec["id"]).save_to_disk(str(spec["dest"]))
    elif spec["source"] == "zenodo":
        log.warning(
            "Zenodo record %s must be downloaded manually into %s "
            "(licence acceptance required).", spec["id"], spec["dest"]
        )


if __name__ == "__main__":
    for k in REGISTRY:
        try:
            download(k)
        except Exception as exc:  # noqa: BLE001
            log.error("Failed %s: %s", k, exc)
