import sys
sys.path.append("src")

from dyslexia.services.stt_service import STTService
from dyslexia.common.text_utils import tokenize
from dyslexia.common.alignment import align
from dyslexia.common.alignment import align, detect_reversals, attach_confidence

TARGET_TEXT = "The cat sat on the warm mat."

print("Loading Whisper...")
stt = STTService(model_size="small")

def run_test(label, audio_path):
    print()
    print("#" * 60)
    print(f"# {label}  ({audio_path})")
    print("#" * 60)

    result = stt.transcribe(audio_path)

    print("TARGET TEXT :", TARGET_TEXT)
    print("WHISPER HEARD:", result["text"])
    print()

    target_tokens = tokenize(TARGET_TEXT)
    spoken_tokens = tokenize(result["text"])
    pairs = align(target_tokens, spoken_tokens)
    pairs = detect_reversals(pairs)
    pairs = attach_confidence(pairs, result["words"])

    print("Word-by-word alignment:")
    for p in pairs:
        conf_str = f"conf={p.confidence:.2f}" if p.confidence is not None else "conf=N/A"
        flag_str = f" [{p.flag}]" if p.flag else ""
        print(f"  target={p.target!r:15} spoken={p.spoken!r:15} op={p.op:12} {conf_str}{flag_str}")
    print()
    print("Word timestamps from Whisper:")
    for w in result["words"]:
        print(f"  {w['word']!r:15} start={w['start']:.2f}s end={w['end']:.2f}s conf={w['prob']:.2f}")

run_test("TEST 4 - INSERTION", "data/raw/m2_pilot/test4.wav")
run_test("TEST 5 - REVERSAL", "data/raw/m2_pilot/test5.wav")