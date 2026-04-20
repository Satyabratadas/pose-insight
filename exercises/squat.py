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