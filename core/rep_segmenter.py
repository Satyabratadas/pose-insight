import numpy as np

class RepSegmenter:
    def __init__(self, exercise="squat", cooldown=15, settle_frames=20):
        self.exercise = exercise
        self.cooldown = cooldown
        self.settle_frames = settle_frames

        # State
        self.state = "up"
        self.valley = None
        self.peak = None
        self.frames_since_rep = 0
        self.rep_count = 0
        self.current_rep_frames = []
        self.settling = False
        self.settle_counter = 0

        # ── Adaptive threshold ──────────────────────────────────────
        # Collect signal for first N frames, then auto-compute thresh
        self.warmup_frames = 30        # observe signal for 30 frames first
        self.warmup_buffer = []        # store signals during warmup
        self.warmed_up = False
        self.depth_thresh = None       # set automatically after warmup

    def _get_signal(self, angles):
        if self.exercise == "squat":
            return angles.get("hip_y")
        else:
            l, r = angles.get("left_elbow"), angles.get("right_elbow")
            valid = [v for v in [l, r] if v is not None]
            return float(np.mean(valid)) if valid else None

    def _compute_threshold(self):
        """
        After warmup, set threshold as 40% of the observed signal range.
        This scales automatically to the video's actual motion amplitude.
        """
        lo = min(self.warmup_buffer)
        hi = max(self.warmup_buffer)
        signal_range = hi - lo

        if signal_range < 0.01:        # person not moving during warmup
            # fallback defaults
            self.depth_thresh = 0.04 if self.exercise == "squat" else 35
        else:
            self.depth_thresh = signal_range * 0.40  # 40% of observed range

        print(f"[RepSegmenter] warmup range={signal_range:.3f} → depth_thresh={self.depth_thresh:.3f}")

    def update(self, angles):
        signal = self._get_signal(angles)
        if signal is None:
            return None

        # ── Warmup phase ────────────────────────────────────────────
        if not self.warmed_up:
            self.warmup_buffer.append(signal)
            self.current_rep_frames.append(angles.copy())
            if len(self.warmup_buffer) >= self.warmup_frames:
                self._compute_threshold()
                self.warmed_up = True
                self.valley = min(self.warmup_buffer)  # init valley from warmup
            return None  # don't count reps during warmup
        # ────────────────────────────────────────────────────────────

        self.current_rep_frames.append(angles.copy())
        self.frames_since_rep += 1

        if self.exercise == "squat":
            return self._update_squat(signal)
        else:
            return self._update_pushup(signal)

    def _update_squat(self, signal):
        if self.state == "up":
            # Settling guard after each rep
            if self.settling:
                self.settle_counter += 1
                if self.settle_counter >= self.settle_frames:
                    self.settling = False
                    self.settle_counter = 0
                    self.valley = signal
                return None

            if self.valley is None:
                self.valley = signal
            self.valley = min(self.valley, signal)

            # Rose enough above valley → going down
            if signal > self.valley + self.depth_thresh:
                self.state = "down"
                self.peak = signal

        elif self.state == "down":
            if self.peak is None:
                self.peak = signal
            self.peak = max(self.peak, signal)

            # Dropped enough below peak → stood back up
            if signal < self.peak - self.depth_thresh:
                if self.frames_since_rep > self.cooldown:
                    self.rep_count += 1
                    rep = self.current_rep_frames[:]
                    self.current_rep_frames = []
                    self.frames_since_rep = 0
                    self.state = "up"
                    self.peak = None
                    self.valley = None
                    self.settling = True
                    self.settle_counter = 0
                    return rep

        return None

    def _update_pushup(self, signal):
        if self.state == "up":
            if self.settling:
                self.settle_counter += 1
                if self.settle_counter >= self.settle_frames:
                    self.settling = False
                    self.settle_counter = 0
                    self.valley = signal
                return None

            if self.valley is None:
                self.valley = signal
            self.valley = max(self.valley, signal)  # track max (arms extended)

            # Dropped enough → going down
            if signal < self.valley - self.depth_thresh:
                self.state = "down"
                self.peak = signal

        elif self.state == "down":
            if self.peak is None:
                self.peak = signal
            self.peak = min(self.peak, signal)  # track min (bottom of pushup)

            # Rose enough → pushed back up
            if signal > self.peak + self.depth_thresh:
                if self.frames_since_rep > self.cooldown:
                    self.rep_count += 1
                    rep = self.current_rep_frames[:]
                    self.current_rep_frames = []
                    self.frames_since_rep = 0
                    self.state = "up"
                    self.peak = None
                    self.valley = None
                    self.settling = True
                    self.settle_counter = 0
                    return rep

        return None