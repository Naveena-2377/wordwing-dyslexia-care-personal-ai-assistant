from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

wiki = Path('data/raw/m3_wikilarge')
src = wiki.joinpath('wiki.full.aner.ori.train.src').read_text(encoding='utf-8', errors='ignore').splitlines()
dst = wiki.joinpath('wiki.full.aner.ori.train.dst').read_text(encoding='utf-8', errors='ignore').splitlines()

tok = AutoTokenizer.from_pretrained('models/m3_simplifier')
model = AutoModelForSeq2SeqLM.from_pretrained('models/m3_simplifier')

# pick 5 pairs from training data where complex and simple actually differ a lot
import re
def words(t): return set(re.findall(r'\w+', t.lower()))

shown = 0
for s, d in zip(src, dst):
    ws, wd = words(s), words(d)
    if not ws or not wd:
        continue
    overlap = len(ws & wd) / len(ws | wd)
    if overlap < 0.6 and 8 < len(s.split()) < 25:
        inputs = tok('simplify: ' + s, return_tensors='pt')
        out_ids = model.generate(**inputs, max_new_tokens=80, num_beams=4)
        out = tok.decode(out_ids[0], skip_special_tokens=True)
        print('SRC     :', s)
        print('TRUE DST:', d)
        print('MODEL   :', out)
        print()
        shown += 1
        if shown >= 5:
            break