import os

try:
    from google import genai
except Exception:
    genai = None


def fallback_feedback(session):
    exercise = session.get("exercise", "unknown").replace("_", " ").title()
    quality = session.get("quality_label", "Unknown")
    risks = session.get("risks", [])
    knee = session.get("knee_angle", 0.0)
    elbow = session.get("elbow_angle", 0.0)
    trunk = session.get("trunk_angle", 0.0)

    risk_text = ", ".join(risks) if risks else "No major injury risks detected."

    return (
        f"Overall quality: {quality}. Exercise: {exercise}. "
        f"Average angles — knee: {knee}°, elbow: {elbow}°, trunk: {trunk}°. "
        f"Risk notes: {risk_text}. Focus on controlled reps, balanced posture, and full range of motion."
    )


def generate_feedback(session):
    if genai is None or not os.getenv("GEMINI_API_KEY"):
        return fallback_feedback(session)

    exercise = session.get("exercise", "unknown").replace("_", " ").title()
    quality = session.get("quality_label", "Unknown")
    risks = session.get("risks", [])
    knee = session.get("knee_angle", 0.0)
    elbow = session.get("elbow_angle", 0.0)
    trunk = session.get("trunk_angle", 0.0)
    reps = session.get("total_reps", 0)

#     prompt = f"""
# You are a fitness coaching assistant for a computer vision exercise analysis app.

# Generate concise, user-friendly feedback based on the session metrics.

# Exercise: {exercise}
# Total reps: {reps}
# Model quality prediction: {quality}
# Average knee angle: {knee} degrees
# Average elbow angle: {elbow} degrees
# Average trunk angle: {trunk} degrees
# Detected risk flags: {risks}

# Rules:
# - Use simple language.
# - Give 3 bullet points maximum.
# - Mention what was good.
# - Mention what to improve.
# - Mention injury risk only as "possible risk", not medical diagnosis.
# - Keep it under 90 words.
# """
    prompt = f"""
    You are an expert AI fitness coach analyzing exercise form.

    User exercise session:
    Exercise: {exercise}
    Overall quality: {quality}
    Average knee angle: {knee} degrees
    Average elbow angle: {elbow} degrees
    Average trunk angle: {trunk} degrees
    Detected risks: {risks}

    Your task:
    Provide detailed, supportive, user-friendly coaching feedback.

    Requirements:
    1. Start with an encouraging summary of overall performance.
    2. Clearly explain what the user did well.
    3. Explain the biggest form mistakes.
    4. Explain how those mistakes may affect performance or injury risk.
    5. Give specific correction tips for next session.
    6. End with motivation.
    7. Keep response between 150–220 words.
    8. Use natural coaching language, not robotic bullet points.
    9. Format in short readable paragraphs or structured bullet sections.

    Tone:
    Professional, motivating, beginner-friendly.
    """

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print("Gemini feedback failed:", e)
        return fallback_feedback(session)
    
def generate_risk_summary(session):
    if genai is None or not os.getenv("GEMINI_API_KEY"):
        risks = session.get("risks", [])
        if not risks:
            return "No major injury-risk patterns were detected. Continue focusing on controlled movement and balanced posture."
        return "Possible risk areas detected: " + ", ".join(risks) + ". Focus on controlled form and avoid pushing through pain."

    exercise = session.get("exercise", "unknown").replace("_", " ").title()
    quality = session.get("quality_label", "Unknown")
    risks = session.get("risks", [])
    knee = session.get("knee_angle", 0.0)
    elbow = session.get("elbow_angle", 0.0)
    trunk = session.get("trunk_angle", 0.0)

    prompt = f"""
You are a fitness safety assistant. Generate a user-friendly injury-risk explanation.

Exercise: {exercise}
Overall quality: {quality}
Average knee angle: {knee} degrees
Average elbow angle: {elbow} degrees
Average trunk angle: {trunk} degrees
Detected risk flags: {risks}

Rules:
- Do not give medical diagnosis.
- Say "possible risk" or "may increase strain".
- Explain why the risk may happen.
- Give 3 practical safety tips.
- Keep it under 100 words.
"""

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print("Gemini risk summary failed:", e)
        risks = session.get("risks", [])
        return "Possible risk areas detected: " + ", ".join(risks)