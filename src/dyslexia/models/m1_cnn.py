"""Module 1 model: small CNN for handwriting letter-reversal classification."""
import torch
import torch.nn as nn


class SmallCNN(nn.Module):
    def __init__(self, num_classes: int = 3, dropout: float = 0.3):
        super().__init__()
        self.features = nn.Sequential(
            self._block(1, 32), self._block(32, 64), self._block(64, 128),
        )
        self.head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Dropout(dropout), nn.Linear(128, num_classes),
        )

    @staticmethod
    def _block(cin: int, cout: int) -> nn.Sequential:
        return nn.Sequential(
            nn.Conv2d(cin, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
            nn.Conv2d(cout, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x))


def build_model(cfg: dict) -> nn.Module:
    if cfg["model"]["arch"] == "resnet18":
        from torchvision.models import resnet18

        m = resnet18(weights=None)
        m.conv1 = nn.Conv2d(1, 64, 7, stride=2, padding=3, bias=False)
        m.fc = nn.Linear(512, cfg["model"]["num_classes"])
        return m
    return SmallCNN(cfg["model"]["num_classes"], cfg["model"]["dropout"])
