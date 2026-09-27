"""Export the CNN to ONNX so the handwriting check can run in-browser/on-device."""
import torch

from dyslexia.common.paths import MODELS
from dyslexia.models.m1_cnn import SmallCNN

model = SmallCNN()
model.load_state_dict(torch.load(MODELS / "m1_handwriting_cnn" / "best.pt",
                                 map_location="cpu"))
model.eval()
torch.onnx.export(
    model, torch.randn(1, 1, 64, 64),
    MODELS / "exported" / "m1_handwriting.onnx",
    input_names=["image"], output_names=["logits"],
    dynamic_axes={"image": {0: "batch"}}, opset_version=17)
print("exported ->", MODELS / "exported" / "m1_handwriting.onnx")
