import numpy as np
from collections import deque, Counter
from exercises.squat import SquatCounter
from exercises.pushup import PushUpCounter


class ExerciseClassifier:
    """
    Window-based exercise classifier with per-exercise phase tracking for rep counting.

    Phase logic:
      Squat  : knee angle goes HIGH → LOW → HIGH  (standing → down → standing)
      Push-up: elbow angle goes HIGH → LOW → HIGH  (extended → down → extended)
    """

    # ── Tuneable thresholds ──────────────────────────────────────────────────
    IDLE_MOTION_THRESHOLD   = 12   # below this → idle regardless of exercise
    MIN_FRAMES_TO_CLASSIFY  = 5    # ramp-up guard

    SQUAT_KNEE_MOTION       = 18   # minimum knee ROM for squat detection
    SQUAT_HIP_MOTION        = 12
    SQUAT_ELBOW_MAX         = 30   # elbows should stay quiet
    SQUAT_TRUNK_MAX         = 50   # trunk upright (degrees from vertical)
    SQUAT_LOWER_UPPER_LEAD  = 15   # lower body must dominate by this margin

    PUSHUP_ELBOW_MOTION     = 22   # minimum elbow ROM for push-up detection
    PUSHUP_TRUNK_MAX        = 25   # trunk nearly horizontal
    PUSHUP_LOWER_MAX        = 20   # legs should stay quiet
    PUSHUP_UPPER_LOWER_LEAD = 8    # upper body must dominate

    # Phase thresholds (fraction of full motion range inside the window)
    SQUAT_DOWN_FRAC  = 0.55   # knee must drop below this fraction → "down"
    SQUAT_UP_FRAC    = 0.80   # knee must rise above this fraction  → "up"
    PUSHUP_DOWN_FRAC = 0.45   # elbow must drop below this fraction → "down"
    PUSHUP_UP_FRAC   = 0.75   # elbow must rise above this fraction → "up"


    def __init__(self, window_size: int = 15, pred_window: int = 8):
        self.window_size = window_size
        self.history:      deque = deque(maxlen=window_size)
        self.pred_history: deque = deque(maxlen=pred_window)
        self.last_stable_label = "idle"

        # ── each exercise has its own counter 
        self.counters = {
            "squat":   SquatCounter(),
            "push_up": PushUpCounter(),
            # future: "pullup": PullUpCounter(), "lunge": LungeCounter()
        }

    # Methods that video_processor.py calls from outside

    def update(self, features: dict | None) -> tuple[str, dict]:
        """
        Feed one frame of joint angles.

        Args:
            features: dict with keys:
                left_knee, right_knee, left_hip, right_hip,
                left_elbow, right_elbow, trunk
              or None (dropped frame).

        Returns:
            (smoothed_label, rep_counts)
        """
        if features is None:
            self.pred_history.append(self.last_stable_label)
            return self.last_stable_label, self._rep_counts()

        self.history.append(features)

        if len(self.history) < self.MIN_FRAMES_TO_CLASSIFY:
            self._append_and_smooth("idle")
            return self.last_stable_label, self._rep_counts()

        raw = self._classify()
        self._update_counter(raw)    ## repetation count
        self._append_and_smooth(raw)
        return self.last_stable_label, self._rep_counts()

    def reset_reps(self) -> None:
        for counter in self.counters.values():
            counter.reset()

    def _rep_counts(self) -> dict:
        return {name: c.reps for name, c in self.counters.items()}

    def _update_counter(self, label: str) -> None:
        if label not in self.counters:
            return

        sig = self._motion_signature()

        if label == "squat":
            knees = sig["_knees"]
            self.counters["squat"].update(knees)

        elif label == "push_up":
            elbows = sig["_elbows"]
            self.counters["push_up"].update(elbows)

    # Classification 

    def _classify(self) -> str:
        sig = self._motion_signature()

        # 1. Idle — nothing meaningful moving
        if sig["total_motion"] < self.IDLE_MOTION_THRESHOLD:
            return "idle"

        # 2. Squat
        #    • Knees and hips dominate  (lower >> upper)
        #    • Elbows quiet
        #    • Trunk upright
        if (
            sig["knee_motion"]  > self.SQUAT_KNEE_MOTION
            and sig["hip_motion"]   > self.SQUAT_HIP_MOTION
            and sig["elbow_motion"] < self.SQUAT_ELBOW_MAX
            and sig["avg_trunk"]    < self.SQUAT_TRUNK_MAX
            and sig["lower_body"]   > sig["upper_body"] + self.SQUAT_LOWER_UPPER_LEAD
        ):
            return "squat"

        # 3. Push-up
        #    • Elbows dominate (upper >> lower)
        #    • Legs / trunk quiet
        #    • Trunk horizontal (large angle from vertical)
        if (
            sig["elbow_motion"] > self.PUSHUP_ELBOW_MOTION
            and sig["lower_body"]   < self.PUSHUP_LOWER_MAX
            and sig["trunk_motion"] < self.PUSHUP_TRUNK_MAX
            and sig["upper_body"]   > sig["lower_body"] + self.PUSHUP_UPPER_LOWER_LEAD
        ):
            return "push_up"

        return "idle"   # ambiguous → treat as idle, NOT "unknown"

    # Motion features

    def _motion_signature(self) -> dict:
        knees, hips, elbows, trunks = [], [], [], []

        for f in self.history:
            knees.append( (f["left_knee"]   + f["right_knee"])  / 2)
            hips.append(  (f["left_hip"]    + f["right_hip"])   / 2)
            elbows.append((f["left_elbow"]  + f["right_elbow"]) / 2)
            trunks.append(f["trunk"])

        knee_motion  = max(knees)  - min(knees)
        hip_motion   = max(hips)   - min(hips)
        elbow_motion = max(elbows) - min(elbows)
        trunk_motion = max(trunks) - min(trunks)

        return {
            "knee_motion":  knee_motion,
            "hip_motion":   hip_motion,
            "elbow_motion": elbow_motion,
            "trunk_motion": trunk_motion,
            "avg_trunk":    float(np.mean(trunks)),
            "lower_body":   knee_motion + hip_motion,
            "upper_body":   elbow_motion,
            "total_motion": knee_motion + hip_motion + elbow_motion,
            "_knees":       knees,
            "_elbows":      elbows,
        }

    def _append_and_smooth(self, label: str) -> None:
        self.pred_history.append(label)
        smoothed = Counter(self.pred_history).most_common(1)[0][0]
        self.last_stable_label = smoothed