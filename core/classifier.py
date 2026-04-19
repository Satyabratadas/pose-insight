import numpy as np
from collections import deque

class ExerciseClassifier:
    def __init__(self, window_size=15):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)

    def update(self, features):
        if features is None:
            return "unknown"

        self.history.append(features)

        if len(self.history) < 5:
            return "idle"
        
        return self.classify()

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
        avg_trunk = np.mean(trunks)

        total_motion = knee_motion + hip_motion + elbow_motion

        # 1. Idle
        if total_motion < 15:
            return "idle"

        # 2. Squat
        if knee_motion > 20 and hip_motion > 15 and elbow_motion < 20 and avg_trunk < 35:
            return "squat"

        # 3. Push-up
        if elbow_motion > 20 and knee_motion < 25:
            return "push_up"

        return "unknown"