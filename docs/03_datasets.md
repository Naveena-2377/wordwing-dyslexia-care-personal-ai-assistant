# Datasets

## Registry

| Module | Dataset | Use | Link |
| --- | --- | --- | --- |
| M1 | Dyslexia Handwriting Dataset | train the reversal CNN | kaggle.com/datasets/drizasazanitaisa/dyslexia-handwriting-dataset |
| M1 | Synthetic Dyslexia Handwriting (YOLO) | augmentation + detection experiments | kaggle.com/datasets/michaelfink0923/synthetic-dyslexia-handwriting-dataset |
| M1 | EMNIST Letters | pretraining before fine-tune | kaggle.com/datasets/crawford/emnist |
| M2 | NNCES corpus (~20h, Indian children reading English) | train/validate reading error detection | kaggle.com/datasets/kodaliradha20phd7093/nonnative-children-english-speech-nnces-corpus |
| M2 | Children's Speech Recording Dataset | held-out validation | zenodo.org/records/200495 |
| M3 | WikiLarge | sentence simplification fine-tune | huggingface.co/datasets/waboucay/wikilarge |
| M4 | *(reuses M1)* | — | — |
| M5 | *(none — integration only)* | — | — |
| M6 | ETDD70 eye-tracking | optional research extension | zenodo.org/records/13332134 |

## The gap these datasets do not fill

**None of them contain labelled dyslexic reading errors from audio.** That is the
exact thing M2 needs. Three ways to close it, used together:

### 1. Synthetic error injection (bulk of training data)

`src/dyslexia/data/synth_reading_errors.py` takes clean sentences and injects
errors with controlled probabilities, keeping the injected type as the label:

- reversal: swap a letter from `b/d p/q m/w n/u`
- omission: drop a function word (`the`, `a`, `of`, `to`)
- mispronunciation: apply a phonetic substitution (`ph→f`, `tion→shun`) or transpose two letters
- slow_decoding: mark long words and assign a long simulated duration

Three severity profiles (mild / moderate / severe) so the model sees a realistic
range rather than one uniform noise level. This is a published technique in
dyslexia NLP, not a shortcut — cite it as such in your report.

### 2. NNCES as real-but-unlabelled data

NNCES gives you real Indian children reading English with the target prompts.
Run ASR + alignment over it and the alignment operations (`match`, `substitution`,
`omission`, `insertion`) become **weak labels** for free. Combine with the
`is_reversal_error` rule and duration thresholds to refine them into your taxonomy.

### 3. Small self-collected pilot set (test set only)

10–30 recordings of children reading fixed passages, with written guardian consent,
hand-labelled by you against the taxonomy. This is your **only honest test set**.
It is small, so report confidence intervals, not a bare accuracy number.

## The split rule

```
TRAIN : synthetic (bulk) + NNCES weak-labelled
VAL   : NNCES held-out speakers
TEST  : hand-labelled pilot recordings ONLY
```

**Split by speaker, never by utterance.** The same child's voice in both train and
test inflates every number you report and a reviewer will ask about it.

## Known data problems to check in `notebooks/00_data_audit.ipynb`

- Kaggle handwriting folders often have inconsistent nesting — verify the class folder names before running preprocessing.
- NNCES sample rates vary; resample everything to 16 kHz mono up front.
- EMNIST images are stored transposed. If your pretrained model collapses, this is why.
- WikiLarge contains noisy pairs where the "simple" sentence is not simpler — filter by Flesch-Kincaid delta before training.
- Class imbalance is severe everywhere: `correct` dominates, `reversal` is rare. Use class weights, report macro-F1.
