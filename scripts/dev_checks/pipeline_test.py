import os, imageio_ffmpeg
os.environ["PATH"] = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()) + os.pathsep + os.environ["PATH"]

import sys
sys.path.append("src")

from dyslexia.inference.pipeline import ReadingSessionPipeline
from dyslexia.inference.predictors import ErrorClassifierPredictor, RiskPredictor
from dyslexia.models.m8_adaptive_coach import AdaptiveCoach
from dyslexia.services.stt_service import STTService
from dyslexia.common.config import load_config

print("Loading models...")
arms = load_config("configs/m8_bandit.yaml")["arms"]
pipeline = ReadingSessionPipeline(
    error_clf=ErrorClassifierPredictor(),
    risk_scorer=RiskPredictor(),
    coach=AdaptiveCoach(arms),
    asr=STTService(model_size="small"),
)

print("Running full session analysis...")
result = pipeline.run(
    audio_path="data/raw/m2_pilot/test1.wav",
    target_text="The cat sat on the warm mat.",
    utt_id="test1",
)

print()
print("=" * 50)
print("FULL SESSION RESULT")
print("=" * 50)
print(f"WPM              : {result.wpm:.1f}")
print(f"Accuracy         : {result.accuracy:.2%}")
print(f"Error rates      : {result.error_rates}")
print(f"Risk score       : {result.risk_score:.3f}")
print(f"Risk band        : {result.risk_band}")
print(f"Next exercise    : {result.next_exercise}")
print()
print("Word-level labels:")
for e in result.word_errors:
    print(f"  {e}")