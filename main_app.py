
import streamlit as st
import tempfile
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

st.set_page_config(page_title="Padel Video Trimmer", layout="wide")
st.title("🎾 Padel Video Trimmer")
st.markdown("Upload your padel match video and we’ll trim out the waiting and walking around automatically!")

uploaded_file = st.file_uploader("Upload your video (.mp4)", type=["mp4"])
min_motion_duration = st.slider("Min Active Segment Duration (sec)", 2, 10, 3)
min_clip_length = st.slider("Min Final Clip Length (sec)", 2, 10, 4)

if uploaded_file:
    with st.spinner("Processing video..."):
        temp_dir = tempfile.mkdtemp()
        input_path = os.path.join(temp_dir, uploaded_file.name)
        with open(input_path, "wb") as f:
            f.write(uploaded_file.read())

        clip = VideoFileClip(input_path)
        duration = clip.duration
        segments = []

        window = 1  # second
        step = 0.5  # seconds
        current = 0
        threshold = 10  # percent difference in frames

        def is_active(start, end):
            try:
                sub = clip.subclip(start, end)
                return sub.std() > 5  # crude motion detection based on std deviation
            except:
                return False

        while current + window <= duration:
            if is_active(current, current + window):
                segment_start = current
                while current + window <= duration and is_active(current, current + window):
                    current += step
                segment_end = current
                if segment_end - segment_start >= min_motion_duration:
                    segments.append((segment_start, segment_end))
            current += step

        trimmed_clips = [clip.subclip(start, end) for start, end in segments if end - start >= min_clip_length]

        if trimmed_clips:
            final_clip = concatenate_videoclips(trimmed_clips)
            output_path = os.path.join(temp_dir, "trimmed_output.mp4")
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

            with open(output_path, "rb") as f:
                st.success("✅ Done! Download your trimmed video below:")
                st.download_button("📥 Download Trimmed Video", f, file_name="trimmed_padel_video.mp4", mime="video/mp4")
        else:
            st.warning("No active gameplay segments detected.")

