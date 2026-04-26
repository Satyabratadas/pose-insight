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

        with st.spinner("Analyzing movement..."):
            success, session = process_video(temp_input.name, output_path)

        if success and os.path.exists(output_path):
            st.success("✅ Analysis Complete")

            with open(output_path, "rb") as f:
                video_bytes = f.read()

            left_col, right_col = st.columns([1.4, 1])

            with left_col:
                st.subheader("🎥 Processed Video")
                st.video(video_bytes)

            with right_col:
                st.subheader("📊 Session Report")

                st.metric("Exercise", session["exercise"].replace("_", " ").title())
                st.metric("Total Reps", session["total_reps"])

                quality_label = session.get("quality_label", "Unknown")
                if "Good" in quality_label:
                    st.success(f"✅ {quality_label}")
                elif "Bad" in quality_label:
                    st.error(f"❌ {quality_label}")
                else:
                    st.info(f"🔍 {quality_label}")

                st.subheader("📐 Average Angles")
                st.metric("Knee", f"{session.get('knee_angle', 0.0)}°")
                st.metric("Elbow", f"{session.get('elbow_angle', 0.0)}°")
                st.metric("Trunk", f"{session.get('trunk_angle', 0.0)}°")

            st.divider()

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
