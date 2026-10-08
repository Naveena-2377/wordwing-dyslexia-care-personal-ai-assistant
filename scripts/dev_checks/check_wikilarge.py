import re
from pathlib import Path

wiki = Path('data/raw/m3_wikilarge')
src = wiki.joinpath('wiki.full.aner.ori.train.src').read_text(encoding='utf-8', errors='ignore').splitlines()
dst = wiki.joinpath('wiki.full.aner.ori.train.dst').read_text(encoding='utf-8', errors='ignore').splitlines()

identical = sum(1 for s, d in zip(src, dst) if s.strip() == d.strip())
print(f'identical pairs: {identical} / {len(src)} = {identical/len(src)*100:.1f}%')

def words(t):
    return set(re.findall(r'\w+', t.lower()))

near_identical = 0
for s, d in zip(src[:20000], dst[:20000]):
    ws, wd = words(s), words(d)
    if ws and wd and len(ws & wd) / len(ws | wd) > 0.9:
        near_identical += 1
print(f'near-identical (sample of 20000): {near_identical} / 20000 = {near_identical/20000*100:.1f}%')