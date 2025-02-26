import streamlit as st
import google.generativeai as genai
import os
import shutil
from dotenv import load_dotenv
import json
from streamlit_option_menu import option_menu
import re
import numpy as np
import requests
import time

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API"))

content_model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instruction="You are the content generator, who can deliver the required information based on the transcript given."
)

vision_model = genai.GenerativeModel(
    'gemini-2.0-flash', 
    system_instruction = "You are a very good video analyzer and information extractor from video"
)

transcription_model = genai.GenerativeModel(
    'gemini-2.0-flash',
    system_instruction = "You are the transcription model, who can convert the given video into text format, and also able to tranlate the transcript"
)

def get_local_path(filename):
    safe_filename = os.path.basename(filename).replace(" ", "_")
    downloads_folder = os.path.join("downloads")
    os.makedirs(downloads_folder, exist_ok=True)    
    return os.path.join(downloads_folder, safe_filename)  

@st.cache_data
def load_url(drive_url):
    file_id = drive_url.split("/d/")[1].split("/")[0]
    direct_link = f"https://drive.google.com/uc?export=download&id={file_id}"
    file_path = get_local_path(f"video_{file_id}.mp4")

    with st.spinner("Checking Google Drive Link..."):
        try:
            response = requests.get(direct_link)  
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                return file_path
            else:
                st.error("Failed to download file from Google Drive")
                return None
        except Exception as e:
            st.error(f"Google Drive download error: {str(e)}")
            return None

def get_from_uploads(video_file):
    file_path = get_local_path(video_file.name)
    with open(file_path, "wb") as f:
        while chunk := video_file.read(1024 * 1024):  
            f.write(chunk)
    return file_path 

def wait_for_file_active(file, max_retries=5, delay=5):
    retries = 0
    while retries < max_retries:
        status = file.state.name
        if status == "ACTIVE":
            return True
        elif status == "FAILED":
            st.error("File upload failed!")
            return False
        time.sleep(delay)
        retries += 1
        file = genai.get_file(file.name)  
    st.error("File activation timed out!")
    return False

def transcribe_video(my_file):
    try:
        response = transcription_model.generate_content([
            """Transcribe this video content. If the video content or transcript is in another language, translate it to English, else don't need to translate. Return STRICT JSON format with: 
            {'Original_text' : string, 
             'Translated_text' : string, 
             'Original_language' : string}""",
            my_file
        ])
        return parse_gemini_response(response.text)

    except Exception as e:
        st.error(f"Transcription failed: {str(e)}")
        return None

def analyze_with_vision(my_file):
    try:
        response = vision_model.generate_content([ 
            """Analyze this video content for any purposes, related to the ideo (It can be educational, entertainment, etc). Return STRICT JSON format with: 
            {genre : string, 
            mood : string, 
            similar_content_suggestions : array of strings, 
            key_elements : array of strings,
            audience_options : array of strings}""",
            my_file
        ])
        my_file.delete()
        return parse_gemini_response(response.text)

    except Exception as e:
        st.error(f"Vision analysis failed: {str(e)}")
        return None

def analyze_type(transcript):
    prompt = f"""By the help of the following text, identify the score of whether it is related educational content or not, the score provided should be in the range of 0 to 1, where higher represents education content
    DO NOT encourage any vulgar or UNUWANTED content required for entertainment purposes like comedy, singing, dancing and all, 
    Always try to look straight on the point, and the tone of the text too, if it is professional and is knowledge related thing, consider it to be educational
    The output format should be a STRICT JSON FORMAT as provided

    'Score : float value between 0 and 1'

    This is the following text : {transcript}"""

    response = content_model.generate_content(prompt)
    return parse_gemini_response(response.text)

def parse_gemini_response(response_text):
    try:
        cleaned = re.sub(r'```json|```', '', response_text)
        cleaned = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', cleaned)
        json_str = re.search(r'\{[\s\S]*\}', cleaned)
        if json_str:
            return json.loads(json_str.group())
        return None

    except Exception as e:
        st.error(f"Failed to parse response: {str(e)}")
        return None

st.set_page_config(page_title="Video Insight AI", layout="wide")

if 'current_video' not in st.session_state:
    st.session_state.current_video = {'id': None, 'type': None}
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = {}
if 'audience' not in st.session_state:
    st.session_state.audience = "General"

st.title("Video Insight AI")
video_file_path = None

with st.sidebar:
    st.title("Video Insight AI")
    option = st.selectbox("Choose the way of uploading the file", 
                         ["Upload a file", "Enter the Google Drive URL"])
    
    if option == "Upload a file":
        video_file = st.file_uploader("Upload a video file", 
                                    type=["mp4", "mov", "avi"], 
                                    help="Upload a file")
        if video_file:
            try:
                video_file_path = get_from_uploads(video_file)
            except Exception as e:
                st.error(f"There is an error loading the file: {e}")
        
        video_id = f"{video_file}_id"

    else:
        video_url = st.text_input("Enter the video URL", 
                                 help="Enter a Google Drive URL")
        
        if video_url:
                try:
                    video_file_path = load_url(video_url)
                except Exception as e:
                    st.error(f"Google Drive access error: {e}")

        video_id = f"{video_url}_id"

    if video_id:
        with st.expander("Video ID Extraction", expanded=True):
            if (st.session_state.current_video['id'] != video_id):
                st.session_state.chat_history[video_id] = []
                st.session_state.current_video = {'id': video_id, 'type': None}
    
        if st.button("Process Video"):

            with st.spinner("Uploading file..."):
                my_file = genai.upload_file(video_file_path)
                if my_file.state.name == "FAILED":
                    print("Re-uploading the file...")
                    my_file = genai.upload_file(video_file_path)

                if not wait_for_file_active(my_file):
                    st.stop()

            with st.spinner("Getting Transcript..."):
                st.session_state.transcript = transcribe_video(my_file)

            with st.spinner("Analyzing Video..."):
                st.session_state.current_video['type'] = "Knowledge Analytics" if analyze_type(st.session_state.transcript['Translated_text'])['Score'] > 0.5 else "Entertainment Analytics"
                st.session_state.analysis = analyze_with_vision(my_file)

            st.success("Video processed successfully!")
                    
if st.session_state.analysis:

    if st.session_state.analysis and 'audience_options' in st.session_state.analysis:
        st.session_state.audience = st.selectbox(
            "Select Audience:",
            options=st.session_state.analysis.get('audience_options', ['General']),
            key='audience_selector'
        )

    if st.session_state.current_video['type'] == "Knowledge Analytics":
        menu_options = ["Summary", "Roadmap", "Transcript", "Chat"]
        st.info("This video consists of educational content")

    else:
        menu_options = ["Summary", "Similar Content", "Transcript", "Chat"]
        st.info("This video consists of entertainment content")

    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=["file-text", "map" if st.session_state.current_video['type'] == "Knowledge Analytics" else "film", 
            "card-text", "chat"],
        default_index=0,
        orientation="horizontal"
    )

    if st.session_state.analysis and video_id:
        if selected == "Summary":
            st.header("Video Summary")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    if st.session_state.current_video['type'] == "Knowledge Analytics":
                        prompt = st.session_state.analysis.get('custom_prompt', 
                            "Provide comprehensive and detailed summary for {st.session_state.audience}")
                        content = st.session_state.transcript['Translated_text']
                    else:
                        prompt = "Provide comprehensive and detailed entertainment analysis summary"
                        content = json.dumps(st.session_state.analysis)
                    
                    response = content_model.generate_content(f"{prompt} for the provided text \n\n{content}")
                    st.write(response.text)
        
        elif selected == "Roadmap" and st.session_state.current_video['type'] == "Knowledge Analytics":
            st.header("Learning Roadmap")
            if st.button("Generate Roadmap"):
                with st.spinner("Creating roadmap..."):
                    response = content_model.generate_content(
                        f"Create learning roadmap for {st.session_state.audience}\n"
                        f"Transcript: {st.session_state.transcript['Translated_text']}"
                    )
                    st.write(response.text)
        
        elif selected == "Similar Content" and st.session_state.current_video['type'] == "Entertainment Analytics":
            st.header("Similar Content Recommendations")
            if st.session_state.analysis:
                st.subheader("Genre: " + st.session_state.analysis.get('genre', ''))
                st.write("Key Elements:", ", ".join(st.session_state.analysis.get('key_elements', [])))
                st.subheader("Recommended Similar Content:")
                for item in st.session_state.analysis.get('similar_content_suggestions', []):
                    st.write(f"- {item}")
        
        elif selected == "Transcript":
            st.header("Video Transcript")
            if st.session_state.transcript:
                if st.session_state.transcript['Original_language'] != 'en' or st.session_state.transcript['Original_language'] != 'English':
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("English Translation")
                        st.write(st.session_state.transcript['Translated_text'])
                    with col2:
                        st.subheader(f"Original ({st.session_state.transcript['Original_language']})")
                        st.write(st.session_state.transcript['Original_text'])
                
                else:
                    st.subheader(f"Original ({st.session_state.transcript['Original_language']})")
                    st.write(st.session_state.transcript['Original_text'])
        
        elif selected == "Chat":
            st.header("Video Chat Assistant")
            current_chat = st.session_state.chat_history.get(video_id, [])
            
            for message in current_chat:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if prompt := st.chat_input("Ask about the content"):
                current_chat.append({"role": "user", "content": prompt})
                
                with st.spinner("Thinking..."):
                    if st.session_state.current_video['type'] == "Knowledge Analytics":
                        context = st.session_state.transcript['Translated_text']
                    else:
                        context = json.dumps(st.session_state.analysis)
                    
                    response = content_model.generate_content("Answer the Question from the given Context with resprct to the given set of Audience\n"
                        f"Audience: {st.session_state.audience}\n"
                        f"Question: {prompt}\n"
                        f"Context: {context}"
                    )
                    current_chat.append({"role": "assistant", "content": response.text})
                
                st.session_state.chat_history[video_id] = current_chat
                
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)

else:
    st.warning("There is no file submitted yet !!")
