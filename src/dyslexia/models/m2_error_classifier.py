"""Module 2 model: BiLSTM over word-level features -> error type per word.

Sequence matters: a child who has just stumbled is more likely to stumble again,
and an omission is often followed by a repetition. A per-word classifier alone
cannot see that; a BiLSTM over the utterance can.
"""
import torch
import torch.nn as nn


class BiLSTMErrorClassifier(nn.Module):
    def __init__(self, input_dim: int, num_labels: int,
                 hidden: int = 128, layers: int = 2, dropout: float = 0.3):
        super().__init__()
        self.proj = nn.Sequential(nn.Linear(input_dim, hidden), nn.ReLU())
        self.lstm = nn.LSTM(hidden, hidden, layers, batch_first=True,
                            bidirectional=True, dropout=dropout)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout), nn.Linear(hidden * 2, num_labels))

    def forward(self, x: torch.Tensor, mask: torch.Tensor | None = None):
        h, _ = self.lstm(self.proj(x))
        return self.classifier(h)          # B, T, num_labels
