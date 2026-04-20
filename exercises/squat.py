class SquatCounter:
    def __init__(self, up_threshold=160, down_threshold=100):
        self.up_threshold = up_threshold
        self.down_threshold = down_threshold
        self.state = "UP"
        self.reps = 0

    def update(self, features):
        if features is None:
            return self.reps, self.state
        
        avg_knee = (features["left_knee"]) + (features["right_knee"]) / 2

        if self.state == "UP" and avg_knee < self.down_threshold:
            self.state = "DOWN"

        elif self.state == "DOWN" and avg_knee > self.up_threshold:
            self.state = "UP"
            self.reps += 1
        
        return self.reps, self.state