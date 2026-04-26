import numpy as np
from collections import deque, Counter
from exercises.squat import SquatCounter, score_squat
from exercises.pushup import PushUpCounter, score_pushup


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

    # ── Posture gate thresholds ──────────────────────────────────────────────
    # Trunk angle is measured from vertical (0° = perfectly upright).
    # If the person is clearly upright  → only squat/idle are possible.
    # If the person is clearly horizontal → only push_up/idle are possible.
    STANDING_TRUNK_MAX   = 45   # avg trunk < 45°  → "standing" zone
    HORIZONTAL_TRUNK_MIN = 55   # avg trunk > 55°  → "horizontal" zone
    # 45°–55° is a neutral dead-band — no zone constraint applied.

    def __init__(self, window_size: int = 15, pred_window: int = 8):
        self.window_size = window_size
        self.history:      deque = deque(maxlen=window_size)
        self.pred_history: deque = deque(maxlen=pred_window)
        self.last_stable_label = "idle"
        self.last_score = {"score": 100, "feedback": [], "risks": []}

        # ── each exercise has its own counter
        self.counters = {
            "squat":   SquatCounter(),
            "push_up": PushUpCounter(),
            # future: "pullup": PullUpCounter(), "lunge": LungeCounter()
        }

    # ── Methods that video_processor.py calls from outside ───────────────────

    def update(self, features: dict | None) -> tuple[str, dict, dict]:
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
            return self.last_stable_label, self._rep_counts(), self.last_score

        self.history.append(features)

        if len(self.history) < self.MIN_FRAMES_TO_CLASSIFY:
            self._append_and_smooth("idle")
            return self.last_stable_label, self._rep_counts()

        raw = self._classify()
        self._update_counter(raw)    # repetition count
        self._append_and_smooth(raw)
        return self.last_stable_label, self._rep_counts(), self.last_score

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

            # Score only when in "down" phase (bottom of squat)
            if self.counters["squat"].phase == "down":
                self.last_score = score_squat(self.history[-1])  # latest frame angles

        elif label == "push_up":
            elbows = sig["_elbows"]
            self.counters["push_up"].update(elbows)

            # Score only when in "down" phase (bottom of push-up)
            if self.counters["push_up"].phase == "down":
                self.last_score = score_pushup(self.history[-1])

    # ── Posture gate ─────────────────────────────────────────────────────────

    def _posture_zone(self, avg_trunk: float) -> str:
        """
        Classify gross body posture from the average trunk angle (degrees from vertical).

        Returns:
            'standing'   → person is upright   → only squat / idle are allowed
            'horizontal' → person is lying down → only push_up / idle are allowed
            'neutral'    → in-between, no constraint applied
        """
        if avg_trunk < self.STANDING_TRUNK_MAX:
            return "standing"
        if avg_trunk > self.HORIZONTAL_TRUNK_MIN:
            return "horizontal"
        return "neutral"

    # ── Classification ────────────────────────────────────────────────────────

    def _classify(self) -> str:
        sig = self._motion_signature()

        # 1. Idle — nothing meaningful moving
        if sig["total_motion"] < self.IDLE_MOTION_THRESHOLD:
            return "idle"

        # ── Posture gate ─────────────────────────────────────────────────────
        # Lock out the wrong exercise class based on how the body is oriented.
        #   • Standing upright  → push_up is impossible, skip that branch entirely
        #   • Lying horizontal  → squat   is impossible, skip that branch entirely
        # This prevents a squat from ever being mislabelled as push_up and vice-versa.
        zone = self._posture_zone(sig["avg_trunk"])

        # 2. Squat
        #    • Knees and hips dominate  (lower >> upper)
        #    • Elbows quiet
        #    • Trunk upright
        #    • Posture gate: skipped when person is clearly horizontal
        if zone != "horizontal" and (
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
        #    • Posture gate: skipped when person is clearly standing
        if zone != "standing" and (
            sig["elbow_motion"] > self.PUSHUP_ELBOW_MOTION
            and sig["lower_body"]   < self.PUSHUP_LOWER_MAX
            and sig["trunk_motion"] < self.PUSHUP_TRUNK_MAX
            and sig["upper_body"]   > sig["lower_body"] + self.PUSHUP_UPPER_LOWER_LEAD
        ):
            return "push_up"

        return "idle"   # ambiguous → treat as idle, NOT "unknown"

    # ── Motion features ───────────────────────────────────────────────────────

    def _motion_signature(self) -> dict:
        knees, hips, elbows, trunks = [], [], [], []

        for f in self.history:
            knees.append( (f["left_knee"]   + f["right_knee"])  / 2)
            hips.append(  (f["left_hip"]    + f["right_hip"])   / 2)
            le, re = f.get("left_elbow"), f.get("right_elbow")
            valid_elbows = [v for v in [le, re] if v is not None]
            elbows.append(float(np.mean(valid_elbows)) if valid_elbows else 0.0)
            trunk = f.get("trunk")
            trunks.append(trunk if trunk is not None else 0.0)

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