"""Module 3 preprocessing: WikiLarge complex/simple pairs -> tokenised dataset.

Source files are plain text, line-aligned by row: wiki.full.aner.ori.{split}.{src,dst}
"""
import re

from ..common.paths import RAW, PROCESSED, ensure
from ..common.logging_utils import get_logger

log = get_logger(__name__)
SRC = RAW / "m3_wikilarge"
DST = PROCESSED / "m3_wikilarge"
MAX_LEN = 96

# known WikiLarge mojibake from a UTF-8/Windows-1252 mismatch
MOJIBAKE_FIXES = {
    "â '' ": "' ", "â€™": "'", "â€˜": "'", "â€œ": '"',
    "â€\x9d": '"', "â€“": "-", "â€”": "-",
}


def clean(text: str) -> str:
    for bad, good in MOJIBAKE_FIXES.items():
        text = text.replace(bad, good)
    return re.sub(r"\s+", " ", text).strip()


def load_pairs(split: str) -> tuple[list[str], list[str]]:
    src = (SRC / f"wiki.full.aner.ori.{split}.src").read_text(
        encoding="utf-8", errors="ignore").splitlines()
    dst = (SRC / f"wiki.full.aner.ori.{split}.dst").read_text(
        encoding="utf-8", errors="ignore").splitlines()
    assert len(src) == len(dst), f"{split}: misaligned src/dst ({len(src)} vs {len(dst)})"
    pairs = [(clean(s), clean(d)) for s, d in zip(src, dst) if s.strip() and d.strip()]
    return [p[0] for p in pairs], [p[1] for p in pairs]


def build(model_name: str = "t5-small") -> None:
    from datasets import Dataset, DatasetDict
    from transformers import AutoTokenizer

    ensure(DST)
    tok = AutoTokenizer.from_pretrained(model_name)

    splits = {}
    for name in ["train", "valid", "test"]:
        complex_, simple_ = load_pairs(name)
        key = "validation" if name == "valid" else name
        splits[key] = Dataset.from_dict({"complex": complex_, "simple": simple_})

    ds = DatasetDict(splits)
    log.info("pairs -> train %d | val %d | test %d",
             len(ds["train"]), len(ds["validation"]), len(ds["test"]))

    def _prep(batch):
        src_in = ["simplify: " + s for s in batch["complex"]]
        model_in = tok(src_in, max_length=MAX_LEN, truncation=True, padding="max_length")
        labels = tok(batch["simple"], max_length=MAX_LEN, truncation=True, padding="max_length")
        model_in["labels"] = [
            [(t if t != tok.pad_token_id else -100) for t in seq]
            for seq in labels["input_ids"]
        ]
        return model_in

    tokenised = ds.map(_prep, batched=True, remove_columns=["complex", "simple"])
    tokenised.save_to_disk(str(DST))
    (DST / "simple_sentences.txt").write_text(
    "\n".join(ds["train"]["simple"][:50000]), encoding="utf-8")
    log.info("tokenised dataset -> %s", DST)


if __name__ == "__main__":
    build()