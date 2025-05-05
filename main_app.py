
import streamlit as st
import cv2
import os
import tempfile
from moviepy.editor import VideoFileClip, concatenate_videoclips
import shutil

st.set_page_config(page_title="Padel Video Trimmer", layout="wide")

st.title("🎾 Padel Video Trimmer")
st.markdown("Upload your padel match video and we’ll trim out the waiting and walking around automatically!")

uploaded_file = st.file_uploader("Upload your video (.mp4)", type=["mp4"])
threshold = st.slider("Motion Detection Sensitivity", 5, 50, 20)
min_motion_duration = st.slider("Min Motion Segment (seconds)", 1, 10, 3)

if uploaded_file:
    with st.spinner("Processing video, please wait..."):
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        motion_segments = []
        segment_start = None
        last_motion_frame = 0
        frame_count = 0

        ret, prev_frame = cap.read()
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)

        progress_bar = st.progress(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(prev_gray, gray)
            non_zero_count = cv2.countNonZero(diff)
            motion_detected = non_zero_count > threshold * 1000

            if motion_detected:
                if segment_start is None:
                    segment_start = frame_count
                last_motion_frame = frame_count
            else:
                if segment_start is not None and (frame_count - last_motion_frame > fps * min_motion_duration):
                    motion_segments.append((segment_start / fps, last_motion_frame / fps))
                    segment_start = None

            prev_gray = gray
            frame_count += 1
            progress = frame_count / cap.get(cv2.CAP_PROP_FRAME_COUNT)
            progress_bar.progress(min(int(progress * 100), 100))

        if segment_start is not None:
            motion_segments.append((segment_start / fps, frame_count / fps))

        cap.release()

        clip = VideoFileClip(input_path)
        trimmed_clips = [clip.subclip(start, end) for start, end in motion_segments]
        if trimmed_clips:
            final_clip = concatenate_videoclips(trimmed_clips)
            output_path = os.path.join(temp_dir, "trimmed_output.mp4")
            final_clip.write_videofile(output_path, codec="libx264")

            with open(output_path, "rb") as f:
                st.success("✅ Done! Download your trimmed video below:")
                st.download_button("📥 Download Trimmed Video", f, file_name="trimmed_padel_video.mp4", mime="video/mp4")
        else:
            st.warning("No motion segments detected based on the current settings.")

        shutil.rmtree(temp_dir)
