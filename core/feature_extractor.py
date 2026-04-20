import numpy as np
from collections import deque

class FeatureExtractor:
    def __init__(self, smooth_window = 5):
        self.smooth_window = smooth_window

        # store history for smoothing
        self.history = {
            "left_knee": deque(maxlen=smooth_window),
            "right_knee": deque(maxlen=smooth_window),
            "left_hip": deque(maxlen=smooth_window),
            "right_hip": deque(maxlen=smooth_window),
            "left_elbow": deque(maxlen=smooth_window),
            "right_elbow": deque(maxlen=smooth_window),
            "hip_y": deque(maxlen=smooth_window),
            "trunk": deque(maxlen=smooth_window)
        }

    # Utility: calculate angle

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        ba = a - b
        bc = c - b

        norm_BA = np.linalg.norm(ba)
        norm_BC = np.linalg.norm(bc)

        ## Add 1e-6 because When two points are the same, When landmarks overlap, 
        # When detection is noisy or missing then norm_BA * norm_BC become 0
        cosine = np.dot(ba, bc) / (norm_BA * norm_BC + 1e-6)
        angle = np.arccos(cosine)
        return np.degrees(angle)

    # Extract key landmarks

    def extract_landmarks(self, results):
        if not results.pose_landmarks:
            return None

        lm = results.pose_landmarks.landmark

        def get_point(idx):
            return (lm[idx].x, lm[idx].y)
        
        return {
            "left_shoulder": get_point(11),
            "right_shoulder": get_point(12),
            "left_elbow": get_point(13),
            "right_elbow": get_point(14),
            "left_wrist": get_point(15),
            "right_wrist": get_point(16),
            "left_hip": get_point(23),
            "right_hip": get_point(24),
            "left_knee": get_point(25),
            "right_knee": get_point(26),
            "left_ankle": get_point(27),
            "right_ankle": get_point(28),
        }
    
    # Compute angles

    def compute_angles(self, lm, vis=None):
        if lm is None:
            return None

        angles = {}

        # Always compute lower-body features
        angles["left_knee"] = self.calculate_angle(
            lm["left_hip"], lm["left_knee"], lm["left_ankle"]
        )
        angles["right_knee"] = self.calculate_angle(
            lm["right_hip"], lm["right_knee"], lm["right_ankle"]
        )

        angles["left_hip"] = self.calculate_angle(
            lm["left_shoulder"], lm["left_hip"], lm["left_knee"]
        )
        angles["right_hip"] = self.calculate_angle(
            lm["right_shoulder"], lm["right_hip"], lm["right_knee"]
        )

        mid_hip = (
            (lm["left_hip"][0] + lm["right_hip"][0]) / 2,
            (lm["left_hip"][1] + lm["right_hip"][1]) / 2,
        )
        angles["hip_y"] = mid_hip[1]

        # Default optional features
        angles["left_elbow"] = None
        angles["right_elbow"] = None
        angles["trunk"] = None

        # Only compute upper-body dependent features if visibility is good
        if vis is not None:
            upper_ok = (
                vis["left_shoulder"] > self.visibility_thresh and
                vis["right_shoulder"] > self.visibility_thresh and
                vis["left_elbow"] > self.visibility_thresh and
                vis["right_elbow"] > self.visibility_thresh and
                vis["left_wrist"] > self.visibility_thresh and
                vis["right_wrist"] > self.visibility_thresh
            )
        else:
            upper_ok = True

        if upper_ok:
            angles["left_elbow"] = self.calculate_angle(
                lm["left_shoulder"], lm["left_elbow"], lm["left_wrist"]
            )
            angles["right_elbow"] = self.calculate_angle(
                lm["right_shoulder"], lm["right_elbow"], lm["right_wrist"]
            )

            mid_shoulder = (
                (lm["left_shoulder"][0] + lm["right_shoulder"][0]) / 2,
                (lm["left_shoulder"][1] + lm["right_shoulder"][1]) / 2,
            )
            mid_hip = (
                (lm["left_hip"][0] + lm["right_hip"][0]) / 2,
                (lm["left_hip"][1] + lm["right_hip"][1]) / 2,
            )

            vertical_ref = (mid_hip[0], mid_hip[1] - 0.1)

            angles["trunk"] = self.calculate_angle(
                mid_shoulder, mid_hip, vertical_ref
            )

        return angles
    
    # Apply smoothing

    def smooth_angles(self, angles):
        if angles is None:
            return None

        smoothed = {}

        for key, value in angles.items():
            if value is None:
                smoothed[key] = None
                continue

            self.history[key].append(value)
            smoothed[key] = float(np.mean(self.history[key]))

        return smoothed
    
    # Main pipeline

    def process(self, results):
        lm = self.extract_landmarks(results)
        if lm is None:
            return None

        angles = self.compute_angles(lm)
        smoothed = self.smooth_angles(angles)

        return smoothed



