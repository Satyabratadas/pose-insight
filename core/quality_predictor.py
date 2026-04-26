import torch
import torch.nn as nn
import numpy as np
from collections import deque

CLASS_NAMES = {
    0: "Good Squat",
    1: "Bad Squat",
    2: "Good Push-up",
    3: "Bad Push-up"
}

class PoseLSTM(nn.Module):
    def __init__(self, input_size=8, hidden_size=64, num_classes=4):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            batch_first=True
        )
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes)
        )

    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)


class QualityPredictor:
    def __init__(self, model_path="models/lstm_quality.pt", seq_len=30):
        self.seq_len = seq_len
        self.buffer = deque(maxlen=seq_len)
        self.last_prediction = "Analyzing..."

        self.model = PoseLSTM(input_size=8, hidden_size=64, num_classes=4)
        self.model.load_state_dict(
            torch.load(model_path, map_location="cpu")
        )
        self.model.eval()

    def update(self, features):
        if features is None:
            return self.last_prediction

        # ── Safe feature extraction — handles None values ─────────────
        feature_vector = [
            float(features.get("left_knee") or 0.0),
            float(features.get("right_knee") or 0.0),
            float(features.get("left_hip") or 0.0),
            float(features.get("right_hip") or 0.0),
            float(features.get("left_elbow") or 0.0),  # None-safe
            float(features.get("right_elbow") or 0.0), # None-safe
            float(features.get("trunk") or 0.0),        # None-safe
            float(features.get("hip_y") or 0.0),
        ]

        self.buffer.append(feature_vector)

        if len(self.buffer) < self.seq_len:
            return "Collecting..."

        # ── Run LSTM ──────────────────────────────────────────────────
        sequence = np.array(list(self.buffer), dtype=np.float32)
        x = torch.tensor(
            sequence.reshape(1, self.seq_len, 8),
            dtype=torch.float32
        )

        with torch.no_grad():
            logits = self.model(x)
            pred = torch.argmax(logits, dim=1).item()

        self.last_prediction = CLASS_NAMES[pred]
        return self.last_prediction

    def predict_rep(self, rep_frames: list) -> str:
        """
        More accurate — predicts on a complete rep
        normalized to exactly 30 frames.
        Call this when RepSegmenter returns a full rep.
        """
        if not rep_frames or len(rep_frames) < 2:
            return self.last_prediction

        from scipy.interpolate import interp1d

        FEATURES = ["left_knee", "right_knee", "left_hip", "right_hip",
                    "left_elbow", "right_elbow", "trunk", "hip_y"]

        arr = np.array(
            [[f.get(k) or 0.0 for k in FEATURES] for f in rep_frames],
            dtype=np.float32
        )  # (T, 8)

        T = arr.shape[0]
        x_old = np.linspace(0, 1, T)
        x_new = np.linspace(0, 1, 30)
        out = np.zeros((30, 8), dtype=np.float32)

        for i in range(8):
            fn = interp1d(x_old, arr[:, i], kind="linear")
            out[:, i] = fn(x_new)

        x = torch.tensor(out).unsqueeze(0)  # (1, 30, 8)
        with torch.no_grad():
            logits = self.model(x)
            pred = torch.argmax(logits, dim=1).item()

        self.last_prediction = CLASS_NAMES[pred]
        return self.last_prediction

    def reset(self):
        self.buffer.clear()
        self.last_prediction = "Analyzing..."