class PushUpCounter:
    def __init__(self):
        self.reps  = 0
        self.phase = "up"

        self.DOWN_FRAC = 0.45
        self.UP_FRAC   = 0.75

    def update(self, elbows: list[float]) -> None:
        lo, hi = min(elbows), max(elbows)
        if hi - lo < 5:
            return

        norm = (elbows[-1] - lo) / (hi - lo)

        if self.phase == "up" and norm < self.DOWN_FRAC:
            self.phase = "down"
        elif self.phase == "down" and norm > self.UP_FRAC:
            self.phase = "up"
            self.reps += 1

    def reset(self):
        self.reps  = 0
        self.phase = "up"

### Scoring Rules

PUSHUP_RULES = [
    {
        "name": "elbow_depth",
        # At bottom of push-up, elbow should bend to ~90°
        # If angle stays > 110° → not going low enough
        "check": lambda a: (
            (a.get("left_elbow") is not None and a["left_elbow"] > 110) or
            (a.get("right_elbow") is not None and a["right_elbow"] > 110)
        ),
        "message": "Go lower — aim for 90° elbow bend",
        "penalty": 20,
        "risk": None,
    },
    {
        "name": "elbow_asymmetry",
        # Big gap between left/right elbow = one arm leading
        "check": lambda a: (
            a.get("left_elbow") is not None and
            a.get("right_elbow") is not None and
            abs(a["left_elbow"] - a["right_elbow"]) > 15
        ),
        "message": "Arms uneven — lower both sides equally",
        "penalty": 20,
        "risk": "shoulder_strain",
    },
    {
        "name": "hip_sag",
        # Trunk angle too large = hips dropping (sagging core)
        "check": lambda a: a.get("trunk") is not None and a["trunk"] > 20,
        "message": "Hips sagging — engage your core and keep body straight",
        "penalty": 25,
        "risk": "lower_back",
    },
    {
        "name": "hip_pike",
        # Trunk angle negative / very small = hips too high (piking)
        "check": lambda a: a.get("trunk") is not None and a["trunk"] < 5,
        "message": "Hips too high — lower them to form a straight line",
        "penalty": 15,
        "risk": None,
    },
]


def score_pushup(angles: dict) -> dict:
    """
    Takes one frame of smoothed angles from FeatureExtractor.
    Returns score, feedback messages, and injury risk flags.

    Usage:
        angles = extractor.process(results)
        result = score_pushup(angles)
        # {"score": 80, "feedback": ["Go lower"], "risks": []}
    """
    score = 100
    feedback = []
    risks = []

    for rule in PUSHUP_RULES:
        try:
            if rule["check"](angles):
                score -= rule["penalty"]
                feedback.append(rule["message"])
                if rule["risk"]:
                    risks.append(rule["risk"])
        except (KeyError, TypeError):
            continue

    return {
        "score": max(score, 0),
        "feedback": feedback,
        "risks": risks,
    }