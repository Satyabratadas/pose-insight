class PushUpCounter:
    def __init__(self, up_threshold=160, down_threshold=90):
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.state = "UP"
        self.reps = 0

    def update(self, features):
        if features is None:
            return self.reps, self.state

        avg_elbow = (features["left_elbow"] + features["right_elbow"]) / 2

        if self.state == "UP" and avg_elbow < self.down_threshold:
            self.state = "DOWN"

        elif self.state == "DOWN" and avg_elbow > self.up_threshold:
            self.state = "UP"
            self.reps += 1

        return self.reps, self.state