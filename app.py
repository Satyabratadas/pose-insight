import streamlit as st
import tempfile
from utils.io_video import process_video, run_webcam
import os

st.title("🏋️ Pose Insight")

options = ["Upload Video", "Live Camera"]
option = st.radio("Select Option", options)
types=["mp4", "mov", "mpeg4"]

if option == options[0]:
    uploaded_file = st.file_uploader(options[0], type= types)
    

    if uploaded_file:
        temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        temp_input.write(uploaded_file.read())
        temp_input.flush()
        temp_input.close()
        file_name = uploaded_file.name
        ## split name and extension
        name, ext = os.path.splitext(file_name)

        output_filename = f"{name}_output{ext}"
        output_path = os.path.join("outputs", output_filename)

        status_text = st.empty()
        status_text.write("Processing...")

        success = process_video(temp_input.name, output_path)

        status_text.empty()

        if success and os.path.exists(output_path):
            st.success("Done!")
            st.write(f"Output file size: {os.path.getsize(output_path)} bytes")

            with open(output_path, "rb") as f:
                video_bytes = f.read()
                
            st.video(video_bytes)
        else:
            st.error("Output video could not be generated.")

elif option == options[1]:
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
