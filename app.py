import streamlit as st
import tempfile
from utils.io_video import process_video, run_webcam
import os

st.title("🏋️ Pose Insight")

options = ["Upload Video", "Live Camera"]
option = st.radio("Select Option", options)
types=["mp4", "mov"]

if option == options[0]:
    uploaded_file = st.file_uploader(options[0], type= types)
    

    if uploaded_file:
        temp_input = tempfile.NamedTemporaryFile(delete=False)
        temp_input.write(uploaded_file.read())
        temp_input.flush()
        temp_input.close()
        file_name = uploaded_file.name
        ## split name and extension
        name, ext = os.path.splitext(file_name)

        output_filename = f"{name}_output{ext}"
        output_path = os.path.join("outputs", output_filename)

        st.write("Processing...")
        process_video(temp_input.name, output_path)

        st.success("Done!")
        with open(output_path, "rb") as f:
            video_bytes = f.read()
        st.video(video_bytes)

elif option == options[1]:
    st.write("Click to start webcam")

    if st.button("Start Camera"):
        run_webcam()