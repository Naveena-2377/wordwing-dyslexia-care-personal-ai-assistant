"""Train the reading error-type classifier.

Train on synthetic + the training split of real data. The TEST set is real
recordings only - a model that only beats synthetic noise proves nothing.
"""
import argparse
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ..common.config import load_config
from ..common.seed import set_seed
from ..common.device import get_device
from ..common.logging_utils import get_logger
from ..common.paths import ROOT as PROJ
from ..models.m2_error_classifier import BiLSTMErrorClassifier

log = get_logger(__name__)


def featurize(word: dict, labels: list[str]) -> list[float]:
    """Hand-crafted per-word features. Keep this function in ONE place -
    training and inference must featurize identically or you get silent skew."""
    from rapidfuzz.distance import Levenshtein

    target, spoken = word.get("target") or "", word.get("spoken") or ""
    return [
        len(target),
        len(spoken),
        Levenshtein.normalized_distance(target, spoken) if spoken else 1.0,
        float(word.get("word_duration", 0.0)),
        float(word.get("asr_prob", 0.0)),
        float(target[:1] == spoken[:1]) if spoken else 0.0,
        float(target[-1:] == spoken[-1:]) if spoken else 0.0,
        float(sum(ch in "bdpqmwnu" for ch in target)),
        float(len(target) > 6),
        float(spoken == ""),
    ]


def load_split(path, labels, max_len=64):
    X, Y, M = [], [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        utt = json.loads(line)
        words = utt["words"] if "words" in utt else [utt]
        if not words:
            continue
        feats = [featurize(wd, labels) for wd in words][:max_len]
        ys = [labels.index(wd["label"]) for wd in words][:max_len]
        pad = max_len - len(feats)
        M.append([1] * len(feats) + [0] * pad)
        X.append(feats + [[0.0] * len(feats[0])] * pad)
        Y.append(ys + [-100] * pad)
    return (torch.tensor(X, dtype=torch.float32),
            torch.tensor(Y), torch.tensor(M))


def main(config: str):
    cfg = load_config(config)
    set_seed(cfg["seed"])
    device = get_device(cfg["device"])
    labels = cfg["labels"]

    syn = PROJ / cfg["data"]["synthetic_dir"] / "synthetic_errors.jsonl"
    X, Y, M = load_split(syn, labels)
    n = len(X); n_val = int(n * cfg["data"]["val_split"])
    Xtr, Ytr, Mtr = X[n_val:], Y[n_val:], M[n_val:]
    Xva, Yva, Mva = X[:n_val], Y[:n_val], M[:n_val]

    model = BiLSTMErrorClassifier(
        input_dim=X.shape[-1], num_labels=len(labels),
        hidden=cfg["model"]["hidden_size"], layers=cfg["model"]["num_layers"],
        dropout=cfg["model"]["dropout"]).to(device)
    crit = nn.CrossEntropyLoss(ignore_index=-100)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["train"]["lr"])

    out_dir = PROJ / cfg["output"]["dir"]; out_dir.mkdir(parents=True, exist_ok=True)
    bs, best = cfg["train"]["batch_size"], 0.0
    for epoch in range(cfg["train"]["epochs"]):
        model.train()
        perm = torch.randperm(len(Xtr))
        for i in range(0, len(Xtr), bs):
            idx = perm[i:i + bs]
            out = model(Xtr[idx].to(device))
            loss = crit(out.reshape(-1, len(labels)), Ytr[idx].reshape(-1).to(device))
            opt.zero_grad(); loss.backward(); opt.step()

        model.eval()
        with torch.no_grad():
            pred = model(Xva.to(device)).argmax(-1).cpu()
        mask = Yva != -100
        acc = (pred[mask] == Yva[mask]).float().mean().item()
        log.info("epoch %02d | val word-acc %.3f", epoch, acc)
        if acc > best:
            best = acc
            torch.save({"state_dict": model.state_dict(), "labels": labels,
                        "input_dim": X.shape[-1]}, out_dir / "best.pt")

    (out_dir / "metrics.json").write_text(json.dumps({"val_word_accuracy": best}, indent=2))
    log.info("best val word-accuracy %.3f", best)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/m2_reading_error.yaml")
    main(ap.parse_args().config)
