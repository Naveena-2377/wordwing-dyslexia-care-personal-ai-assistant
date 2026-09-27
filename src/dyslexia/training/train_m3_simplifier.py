"""Fine-tune T5-small on WikiLarge for sentence simplification."""
import argparse

from ..common.config import load_config
from ..common.paths import ROOT as PROJ
from ..common.logging_utils import get_logger

log = get_logger(__name__)


def main(config: str):
    from datasets import load_from_disk
    from transformers import (AutoModelForSeq2SeqLM, AutoTokenizer,
                              DataCollatorForSeq2Seq, Seq2SeqTrainer,
                              Seq2SeqTrainingArguments)

    cfg = load_config(config)
    base = cfg["model"]["base"]
    ds = load_from_disk(str(PROJ / cfg["data"]["dataset"]))
    tok = AutoTokenizer.from_pretrained(base)
    model = AutoModelForSeq2SeqLM.from_pretrained(base)
    out_dir = PROJ / cfg["output"]["dir"]

    args = Seq2SeqTrainingArguments(
        output_dir=str(out_dir),
        num_train_epochs=cfg["train"]["epochs"],
        per_device_train_batch_size=cfg["train"]["batch_size"],
        gradient_accumulation_steps=cfg["train"]["gradient_accumulation"],
        learning_rate=cfg["train"]["lr"],
        fp16=cfg["train"]["fp16"],
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        predict_with_generate=True,
        logging_steps=100,
    )
    Seq2SeqTrainer(
        model=model, args=args,
        train_dataset=ds["train"], eval_dataset=ds["validation"],
        data_collator=DataCollatorForSeq2Seq(tok, model=model),
    ).train()
    model.save_pretrained(out_dir); tok.save_pretrained(out_dir)
    log.info("simplifier saved -> %s", out_dir)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/m3_simplifier.yaml")
    main(ap.parse_args().config)
