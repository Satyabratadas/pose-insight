import numpy as np
from scipy.interpolate import interp1d

FEATURES = ["left_knee", "right_knee", "left_hip", "right_hip",
            "left_elbow", "right_elbow", "trunk", "hip_y"]

N_FRAMES = 30

def rep_to_vector(rep_frames):
    arr = []
    for f in rep_frames:
        row = [f.get(k) or 0.0 for k in FEATURES]
        arr.append(row)
    arr = np.array(arr)

    T = arr.shape[0]
    if T < 2:
        # Rep too short to interpolate — pad with zeros
        return np.zeros(N_FRAMES * len(FEATURES))

    x_old = np.linspace(0, 1, T)
    x_new = np.linspace(0, 1, N_FRAMES)
    out = np.zeros((N_FRAMES, len(FEATURES)))

    for i in range(len(FEATURES)):
        f = interp1d(x_old, arr[:, i], kind='linear')
        out[:, i] = f(x_new)

    return out.flatten()