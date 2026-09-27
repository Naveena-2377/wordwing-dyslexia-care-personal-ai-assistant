"""Train the handwriting reversal CNN.

Two-stage: optional EMNIST pretrain (learn 'what letters look like'), then
fine-tune on the dyslexia dataset (learn 'what a reversed letter looks like').
"""
import argparse
import json
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import classification_report, confusion_matrix

from ..common.config import load_config
from ..common.seed import set_seed
from ..common.device import get_device
from ..common.logging_utils import get_logger
from ..common.paths import ROOT as PROJ
from ..models.m1_cnn import build_model

log = get_logger(__name__)


def loaders(cfg):
    d = np.load(PROJ / cfg["data"]["processed_dir"] / "m1_data.npz", allow_pickle=True)
    bs = cfg["train"]["batch_size"]
    def mk(split, shuffle):
        return DataLoader(
            TensorDataset(torch.tensor(d[f"X_{split}"]), torch.tensor(d[f"y_{split}"]).long()),
            batch_size=bs, shuffle=shuffle)
    return mk("train", True), mk("val", False), mk("test", False), list(d["classes"])


def run_epoch(model, loader, criterion, device, optimizer=None):
    train = optimizer is not None
    model.train() if train else model.eval()
    total, correct, loss_sum = 0, 0, 0.0
    preds_all, labels_all = [], []
    with torch.set_grad_enabled(train):
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            out = model(xb)
            loss = criterion(out, yb)
            if train:
                optimizer.zero_grad(); loss.backward(); optimizer.step()
            loss_sum += loss.item() * len(yb)
            preds = out.argmax(1)
            correct += (preds == yb).sum().item(); total += len(yb)
            preds_all += preds.cpu().tolist(); labels_all += yb.cpu().tolist()
    return loss_sum / total, correct / total, preds_all, labels_all


def main(config: str):
    cfg = load_config(config)
    set_seed(cfg["seed"])
    device = get_device(cfg["device"])
    tr, va, te, classes = loaders(cfg)
    model = build_model(cfg).to(device)

    # class imbalance is the norm here - reversal samples are the minority
    counts = np.bincount([y for _, yb in tr for y in yb.tolist()],
                         minlength=len(classes))
    weights = torch.tensor((counts.sum() / (len(classes) * np.maximum(counts, 1))),
                           dtype=torch.float32, device=device)
    criterion = nn.CrossEntropyLoss(weight=weights)
    opt = torch.optim.AdamW(model.parameters(), lr=cfg["train"]["lr"],
                            weight_decay=cfg["train"]["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, cfg["train"]["epochs"])

    out_dir = PROJ / cfg["output"]["dir"]; out_dir.mkdir(parents=True, exist_ok=True)
    best, patience = 0.0, 0
    for epoch in range(cfg["train"]["epochs"]):
        trl, tra, *_ = run_epoch(model, tr, criterion, device, opt)
        vll, vla, *_ = run_epoch(model, va, criterion, device)
        sched.step()
        log.info("epoch %02d | train %.4f/%.3f | val %.4f/%.3f",
                 epoch, trl, tra, vll, vla)
        if vla > best:
            best, patience = vla, 0
            torch.save(model.state_dict(), out_dir / "best.pt")
        else:
            patience += 1
            if patience >= cfg["train"]["early_stopping_patience"]:
                log.info("early stop at epoch %d", epoch); break

    model.load_state_dict(torch.load(out_dir / "best.pt"))
    _, acc, preds, labels = run_epoch(model, te, criterion, device)
    report = classification_report(labels, preds, target_names=classes,
                                   output_dict=True, zero_division=0)
    (out_dir / "metrics.json").write_text(json.dumps(
        {"test_accuracy": acc, "report": report,
         "confusion_matrix": confusion_matrix(labels, preds).tolist()}, indent=2))
    log.info("test accuracy %.3f | metrics -> %s", acc, out_dir / "metrics.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/m1_handwriting.yaml")
    main(ap.parse_args().config)
