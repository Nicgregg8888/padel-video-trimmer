
# Padel Video Trimmer 🎾

This is a Streamlit web app that automatically trims padel match videos by detecting motion and removing idle periods.

## Features
- Upload `.mp4` video
- Detects active gameplay using motion
- Trims out idle/waiting parts
- Lets you download the cleaned-up video
- Runs fully on Streamlit Cloud (no local setup needed)

## To Run Locally
```bash
pip install -r requirements.txt
streamlit run main_app.py
```

## To Deploy on Streamlit Cloud
1. Fork or upload this repo to your GitHub.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud).
3. Click **'New app'**, choose this repo, and deploy.
