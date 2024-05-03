import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import os

st.title("Video Transcription")
st.write("The spoken word holds immense value, but capturing it from videos can be a challenge. Here's where video transcription with AI enters the scene, acting as a bridge between audio and text. These tools leverage the power of machine learning to automatically convert spoken content in videos into written text.")
st.markdown("---")

def extract_transcript(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[-1]

        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        transcript_text = ""
        for i in transcript:
            transcript_text += " " + i["text"]

        return transcript_text
    except Exception as e:
        print(f"Error extracting transcript: {e}")
        return None
    

videoURL = st.text_input(label="Enter Video URL", placeholder="Enter A valid Video URL from Youtube ")
if videoURL != None and videoURL and videoURL != "":
    transcription_text = extract_transcript(videoURL)
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    prompt = """
        Title: Detailed Notes on the YouTube Video Transcript
        Your task is to provide detailed notes based on the transcript of a YouTube video I'll provide. Assume the role of a student and generate comprehensive notes covering the key concepts discussed in the video.
        Your notes should:
        - Analyze and explain the main ideas, theories, or concepts presented in the video.
        - Provide examples, illustrations, or case studies to support the understanding of the topic.
        - Offer insights or practical applications of the subject matter discussed.
        - Use clear language and concise explanations to facilitate learning.
    """.format()
    response = model.generate_content(prompt + transcription_text)
    st.markdown(response.text)
    
else:
    st.write("Please enter a valid YouTube video URL")