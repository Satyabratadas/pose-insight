import numpy as np
from collections import deque, Counter

class ExerciseClassifier:
    def __init__(self, window_size=15, pred_window=5):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        self.pred_history = deque(maxlen=pred_window)
        self.last_stable_label = "idle"

    def update(self, features):
        if features is None:
            return "unknown"

        self.history.append(features)

        # Not enough frames → assume idle
        if len(self.history) < 5:
            return "idle"

        # Step 1: get raw prediction
        pred = self.classify()

        # if current prediction is unknown, keep previous stable label
        if pred == "unknown":
            pred = self.last_stable_label
        else:
            self.last_stable_label = pred

        # Step 2: store prediction
        self.pred_history.append(pred)

        # Step 3: return majority vote (smoothed)
        smoothed = Counter(self.pred_history).most_common(1)[0][0]
        self.last_stable_label = smoothed
        return Counter(self.pred_history).most_common(1)[0][0]

    def classify(self):
        knees = []
        hips = []
        elbows = []
        trunks = []

        for f in self.history:
            knees.append((f["left_knee"] + f["right_knee"]) / 2)
            hips.append((f["left_hip"] + f["right_hip"]) / 2)
            elbows.append((f["left_elbow"] + f["right_elbow"]) / 2)
            trunks.append(f["trunk"])

        knee_motion = max(knees) - min(knees)
        hip_motion = max(hips) - min(hips)
        elbow_motion = max(elbows) - min(elbows)
        trunk_motion = max(trunks) - min(trunks)

        avg_trunk = np.mean(trunks)

        lower_body_motion = knee_motion + hip_motion
        upper_body_motion = elbow_motion
        total_motion = lower_body_motion + upper_body_motion

        # 1. Idle
        if total_motion < 15:
            return "idle"

        # 2. Squat
        if (
            knee_motion > 15 and
            hip_motion > 10 and
            lower_body_motion > upper_body_motion + 10 and
            avg_trunk < 45 and
            elbow_motion < 25
        ):
            return "squat"

        # 3. Push-up
        if (
            elbow_motion > 20 and
            upper_body_motion > lower_body_motion + 5 and
            trunk_motion < 20 and
            avg_trunk > 50
        ):
            return "push_up"

        return "unknown"