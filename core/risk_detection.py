def detect_risks(features, quality_label="Unknown"):
    """
    Returns simple injury/form risk flags based on pose angles.
    features: current frame feature dictionary
    quality_label: Good/Bad Squat/Push-up from model
    """

    if features is None:
        return []

    risks = []

    left_knee = features.get("left_knee", 0.0) or 0.0
    right_knee = features.get("right_knee", 0.0) or 0.0
    left_elbow = features.get("left_elbow", 0.0) or 0.0
    right_elbow = features.get("right_elbow", 0.0) or 0.0
    trunk = features.get("trunk", 0.0) or 0.0

    knee_diff = abs(left_knee - right_knee)
    elbow_diff = abs(left_elbow - right_elbow)

    # -------------------------
    # Squat risks
    # -------------------------
    if "Squat" in quality_label:
        avg_knee = (left_knee + right_knee) / 2

        if avg_knee > 135:
            risks.append("Shallow squat depth")

        if trunk > 45:
            risks.append("Forward lean / lower back strain risk")

        if knee_diff > 20:
            risks.append("Knee asymmetry / knee strain risk")

    # -------------------------
    # Push-up risks
    # -------------------------
    elif "Push-up" in quality_label:
        avg_elbow = (left_elbow + right_elbow) / 2

        if avg_elbow > 130:
            risks.append("Incomplete push-up depth")

        if trunk > 60:
            risks.append("Core instability / body alignment risk")

        if elbow_diff > 20:
            risks.append("Elbow asymmetry / shoulder strain risk")

    return risks