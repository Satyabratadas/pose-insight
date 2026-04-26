# ─── Rep Counter (your existing code, unchanged) ───────────────────────────

class SquatCounter:
    def __init__(self):
        self.reps  = 0
        self.phase = "up"

        self.DOWN_FRAC = 0.55
        self.UP_FRAC   = 0.80

    def update(self, knees: list[float]) -> None:
        lo, hi = min(knees), max(knees)
        if hi - lo < 5:
            return

        norm = (knees[-1] - lo) / (hi - lo)

        if self.phase == "up" and norm < self.DOWN_FRAC:
            self.phase = "down"
        elif self.phase == "down" and norm > self.UP_FRAC:
            self.phase = "up"
            self.reps += 1

    def reset(self):
        self.reps  = 0
        self.phase = "up"


### Scoring Rules

SQUAT_RULES = [
    {
        "name": "knee_depth",
        # At bottom of squat, knee angle should be <= 110° (ideally ~90°)
        # If still > 110° at lowest point → not squatting deep enough
        "check": lambda a: a["left_knee"] > 110 or a["right_knee"] > 110,
        "message": "Squat deeper — aim for 90° knee bend",
        "penalty": 20,
        "risk": None,
    },
    {
        "name": "knee_asymmetry",
        # Big difference between left/right knee = one knee caving or lagging
        "check": lambda a: abs(a["left_knee"] - a["right_knee"]) > 15,
        "message": "Knees uneven — push both knees out equally",
        "penalty": 25,
        "risk": "knee_strain",
    },
    {
        "name": "hip_asymmetry",
        # Hips should stay level — big difference = hip shift
        "check": lambda a: abs(a["left_hip"] - a["right_hip"]) > 15,
        "message": "Hips shifting — keep weight evenly distributed",
        "penalty": 15,
        "risk": "hip_strain",
    },
    {
        "name": "forward_lean",
        # Trunk angle > 45° from vertical = excessive forward lean
        "check": lambda a: a.get("trunk") is not None and a["trunk"] > 45,
        "message": "Too much forward lean — keep chest up",
        "penalty": 15,
        "risk": "lower_back",
    },
]


def score_squat(angles: dict) -> dict:
    """
    Takes one frame of smoothed angles from FeatureExtractor.
    Returns score, feedback messages, and injury risk flags.

    Usage:
        angles = extractor.process(results)
        result = score_squat(angles)
        # {"score": 75, "feedback": ["Squat deeper"], "risks": []}
    """
    score = 100
    feedback = []
    risks = []

    for rule in SQUAT_RULES:
        try:
            if rule["check"](angles):
                score -= rule["penalty"]
                feedback.append(rule["message"])
                if rule["risk"]:
                    risks.append(rule["risk"])
        except (KeyError, TypeError):
            # Skip rule if angle data is missing for this frame
            continue

    return {
        "score": max(score, 0),
        "feedback": feedback,
        "risks": risks,
    }