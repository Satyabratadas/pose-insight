import os
import tempfile

import streamlit as st

from utils.io_video import process_video, run_webcam
from core.feedback_generator import generate_feedback, generate_risk_summary


st.title("🏋️ Pose Insight")

options = ["Upload Video", "Live Camera"]
option = st.radio("Select Option", options)

video_types = ["mp4", "mov", "mpeg4"]

if option == "Upload Video":
    uploaded_file = st.file_uploader("Upload Video", type=video_types)

    if uploaded_file:
        os.makedirs("outputs", exist_ok=True)

        file_name = uploaded_file.name
        name, ext = os.path.splitext(file_name)

        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
        temp_input.write(uploaded_file.read())
        temp_input.flush()
        temp_input.close()

        output_filename = f"{name}_output.mp4"
        output_path = os.path.join("outputs", output_filename)

        status_text = st.empty()
        status_text.write("Processing...")

        success, session = process_video(temp_input.name, output_path)

        status_text.empty()

        if success and os.path.exists(output_path):
            st.success("✅ Done!")
            st.write(f"Output file size: {os.path.getsize(output_path)} bytes")

            with open(output_path, "rb") as f:
                video_bytes = f.read()

            st.video(video_bytes)

            st.subheader("📊 Session Report")

            # col1, col2, col3 = st.columns(3)
            # col1.metric("Exercise", session["exercise"].replace("_", " ").title())
            # col2.metric("Total Reps", session["total_reps"])
            # col3.metric("Avg Form Score", f"{session['avg_score']}/100")

            col1, col2 = st.columns(2)
            col1.metric("Exercise", session["exercise"].replace("_", " ").title())
            col2.metric("Total Reps", session["total_reps"])

            st.subheader("📐 Average Joint Angles")

            col4, col5, col6 = st.columns(3)
            col4.metric("Avg Knee Angle", f"{session.get('knee_angle', 0.0)}°")
            col5.metric("Avg Elbow Angle", f"{session.get('elbow_angle', 0.0)}°")
            col6.metric("Avg Trunk Angle", f"{session.get('trunk_angle', 0.0)}°")

            quality_label = session.get("quality_label", "Unknown")

            if "Good" in quality_label:
                st.success(f"✅ Overall Quality: {quality_label}")
            elif "Bad" in quality_label:
                st.error(f"❌ Overall Quality: {quality_label}")
            else:
                st.info(f"🔍 Quality: {quality_label}")

            st.subheader("💬 Coaching Feedback")

            feedback_text = generate_feedback(session)

            st.info(feedback_text)

            st.subheader("⚠️ Injury Risk Summary")

            risk_summary = generate_risk_summary(session)

            if session.get("risks"):
                st.warning(risk_summary)
            else:
                st.success(risk_summary)

        else:
            st.error("Output video could not be generated.")


elif option == "Live Camera":
    st.write("Live webcam feed")

    if "run_camera" not in st.session_state:
        st.session_state.run_camera = False

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start Camera"):
            st.session_state.run_camera = True

    with col2:
        if st.button("Stop Camera"):
            st.session_state.run_camera = False

    frame_placeholder = st.empty()

    if st.session_state.run_camera:
        run_webcam(frame_placeholder, lambda: not st.session_state.run_camera)
