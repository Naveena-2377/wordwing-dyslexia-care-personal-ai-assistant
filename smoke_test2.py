import sys
sys.path.append("src")

from dyslexia.services.stt_service import STTService
from dyslexia.common.text_utils import tokenize
from dyslexia.common.alignment import align

TARGET_TEXT = "The cat sat on the warm mat."

print("Loading Whisper...")
stt = STTService(model_size="small")

print("Transcribing your recording...")
result = stt.transcribe("data/raw/m2_pilot/test2.wav")

print()
print("=" * 50)
print("TARGET TEXT :", TARGET_TEXT)
print("WHISPER HEARD:", result["text"])
print("=" * 50)
print()

target_tokens = tokenize(TARGET_TEXT)
spoken_tokens = tokenize(result["text"])
pairs = align(target_tokens, spoken_tokens)

print("Word-by-word alignment:")
for p in pairs:
    print(f"  target={p.target!r:15} spoken={p.spoken!r:15} op={p.op}")