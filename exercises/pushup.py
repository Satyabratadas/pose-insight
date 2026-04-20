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