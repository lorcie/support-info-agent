"""
Speaker Agent Chat Application
==============================

This Streamlit application provides a chat interface for interacting with the ADK Speaker Agent.
It allows users to create sessions, send messages, and receive both text and audio responses.

Requirements:
------------
- ADK API Server running on localhost:8000
- Speaker Agent registered and available in the ADK
- Streamlit and related packages installed

Usage:
------
1. Start the ADK API Server: `adk api_server`
2. Ensure the Speaker Agent is registered and working
3. Run this Streamlit app: `streamlit run apps/speaker_app.py`
4. Click "Create Session" in the sidebar
5. Start chatting with the Speaker Agent

Architecture:
------------
- Session Management: Creates and manages ADK sessions for stateful conversations
- Message Handling: Sends user messages to the ADK API and processes responses
- Audio Integration: Extracts audio file paths from responses and displays players

API Assumptions:
--------------
1. ADK API Server runs on localhost:8000
2. Speaker Agent is registered with app_name="speaker"
3. The Speaker Agent uses ElevenLabs TTS and saves audio files locally
4. Audio files are accessible from the path returned in the API response
5. Responses follow the ADK event structure with model outputs and function calls/responses

"""
import streamlit as st
import requests
import json
import os
import uuid
import time

voice_character_list={
    "Xb7hH8MSUJpSbSDYk0k2":"Alice-female,middle-aged,British,confident,news",
    "9BWtsMINqrJLrRacOk9x":"Aria-female,middle-aged,American,expressive,social-media",
    "pqHfZKP75CvOlQylNhV4":"Bill-male,old,American,trustworthy,narration",
    "nPczCjzI2devNBz1zQrb":"Brian-male,middle-aged,American,deep,narration",
    "N2lVS1w4EtoT3dr4eOWO":"Callum-male,middle-aged,Transatlantic,intense,characters",
    "IKne3meq5aSn9XLyUdCD":"Charlie-male,middle-aged,Australian,natural,conversational",
    "XB0fDUnXU5powFXDhCwa":"Charlotte-female,young,Swedish,seductive,characters",
    "iP95p4xoKVk53GoZ742B":"Chris-male,middle-aged,American,casual,conversational",
    "onwK4e9ZLuTAKqWW03F9":"Daniel-male,middle-aged,British,authoritative,news",
    "cjVigY5qzO86Huf0OWal":"Eric-male,middle-aged,American,friendly,conversational",
    "JBFqnCBsd6RMkjVDRZzb":"George-male,middle-aged,British,warm,narration",
    "cgSgspJ2msm6clMCkdW9":"Jessica-female,young,American,expressive,conversational",
    "FGY2WhTYpPnrIDTdsKH5":"Laura-female,young,American,upbeat,social-media",
    "TX3LPaxmHKxFdv7VOQHJ":"Liam-male,young,American,articulate,narration",
    "pFZP5JQG7iQjIQuC4Bku":"Lily-female,middle-aged,British,warm,narration",
    "XrExE9yKIg1WjnnlVkGX":"Matilda-female,middle-aged,American,friendly,narration",
    "SAz9YHcvj6GT2YYXdXww":"River-non-binary,middle-aged,American,confident,social-media",
    "CwhRBWXzGAHq8TQ4Fs17":"Roger-male,middle-aged,American,confident,social-media",
    "EXAVITQu4vr4xnSDxMaL":"Sarah-female,young,American,soft,news",
    "bIHbv24MWmeRgasZH58o":"Will-male,young,American,friendly,social-media",
}

    
def voice_character_format_func(option):
    return voice_character_list[option]

# Set page config
st.set_page_config(
    page_title="Speaker Agent Chat",
    page_icon="🔊",
    layout="centered"
)

# Constants
API_BASE_URL = os.getenv("API_BASE_URL","http://localhost:8000")
APP_NAME = os.environ.get("AGENT_APP_NAME","multi_tools_agent")

# Initialize session state variables
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user-{uuid.uuid4()}"
    
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    
if "messages" not in st.session_state:
    st.session_state.messages = []

if "audio_files" not in st.session_state:
    st.session_state.audio_files = []

def create_session():
    """
    Create a new session with the speaker agent.
    
    This function:
    1. Generates a unique session ID based on timestamp
    2. Sends a POST request to the ADK API to create a session
    3. Updates the session state variables if successful
    
    Returns:
        bool: True if session was created successfully, False otherwise
    
    API Endpoint:
        POST /apps/{app_name}/users/{user_id}/sessions/{session_id}
    """
    session_id = f"session-{int(time.time())}"
    response = requests.post(
        f"{API_BASE_URL}/apps/{APP_NAME}/users/{st.session_state.user_id}/sessions/{session_id}",
        headers={"Content-Type": "application/json"},
        data=json.dumps({})
    )
    
    if response.status_code == 200:
        st.session_state.session_id = session_id
        st.session_state.messages = []
        st.session_state.audio_files = []
        return True
    else:
        st.error(f"Failed to create session: {response.text}")
        return False

def send_message(message):
    """
    Send a message to the speaker agent and process the response.
    
    This function:
    1. Adds the user message to the chat history
    2. Sends the message to the ADK API
    3. Processes the response to extract text and audio information
    4. Updates the chat history with the assistant's response
    
    Args:
        message (str): The user's message to send to the agent
        
    Returns:
        bool: True if message was sent and processed successfully, False otherwise
    
    API Endpoint:
        POST /run
        
    Response Processing:
        - Parses the ADK event structure to extract text responses
        - Looks for text_to_speech function responses to find audio file paths
        - Adds both text and audio information to the chat history
    """
    if not st.session_state.session_id:
        st.error("No active session. Please create a session first.")
        return False
    
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Send message to API
    response = requests.post(
        f"{API_BASE_URL}/run",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "app_name": APP_NAME,
            "user_id": st.session_state.user_id,
            "session_id": st.session_state.session_id,
            "new_message": {
                "role": "user",
                "parts": [{"text": message}]
            }
        })
    )
    
    if response.status_code != 200:
        st.error(f"Error: {response.text}")
        return False
    
    # Process the response
    events = response.json()
    
    # Extract assistant's text response
    assistant_message = None
    audio_file_path = None
    
    for event in events:
        # Look for the final text response from the model
        if event.get("content", {}).get("role") == "model" and "text" in event.get("content", {}).get("parts", [{}])[0]:
            assistant_message = event["content"]["parts"][0]["text"]
        
        # Look for text_to_speech function response to extract audio file path
        if "functionResponse" in event.get("content", {}).get("parts", [{}])[0]:
            func_response = event["content"]["parts"][0]["functionResponse"]
            if func_response.get("name") == "get_voice_response":
                response_text = func_response.get("response", {}).get("result", {}).get("content", [{}])[0].get("text", "")
                # Extract file path using simple string parsing
                if "saved at:" in response_text:
                    parts = response_text.split("saved at:")[1].strip().split()
                    if parts:
                        audio_file_path = parts[0].strip(".")
    
    # Add assistant response to chat
    if assistant_message:
        st.session_state.messages.append({"role": "assistant", "content": assistant_message, "audio_path": audio_file_path})
    
    return True

# UI Components
st.title("🔊 Speaker Agent Chat")

# Sidebar for session management
with st.sidebar:
    #st.caption("Session>")
    if st.session_state.session_id:
        st.success(f"Active Session: {st.session_state.session_id}")
    else:
        st.warning("No Active Session")
    if st.button("➕ Create Session"):
        create_session()
    
    #st.divider()

    st.header("Voice Settings (To Develop)")
    voice_character_option = st.selectbox("select voice character:",
        list(voice_character_list.keys()), format_func=voice_character_format_func
    )
    voice_stability = st.slider('Stability>', 0.0, 1.0, 0.5)
    voice_use_speaker_boost=st.radio('Use Speaker Boost>', [True, False], horizontal=True)
    voice_similarity_boost = st.slider('Similarity Boost>', 0.0, 1.0, 0.75)
    voice_style = st.slider('Style>', 0.0, 1.0, 0.0)
    voice_speed = st.slider('Speed>', 0.0, 1.0, 1.0)



# Chat interface
st.subheader("Conversation")

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])
            
            # Handle audio if available
            if "audio_path" in msg and msg["audio_path"]:
                audio_path = msg["audio_path"]
                print(f"audio_path_extracted<{audio_path}>")
                if os.path.exists(audio_path):
                    st.audio(audio_path)
                else:
                    #temporary fix
                    default_audio_path="output/audio-test.mp3"
                    if os.path.exists(default_audio_path):
                        st.audio(default_audio_path)
                    else:
                        st.warning(f"Audio file not accessible: <{audio_path}>")

last_user_message = ""
# Input for new messages
if st.session_state.session_id:  # Only show input if session exists
    user_input = st.chat_input("Type your message...")
    if user_input is not None and last_user_message != user_input:
        send_message(user_input+f" with voice_id:{voice_character_option}")
        last_user_message = user_input
        st.rerun()  # Rerun to update the UI with new messages
else:
    st.info("👈 Create a session to start chatting")
    st.write(f"Current Voice Character option: {voice_character_option} attributes: {voice_character_format_func(voice_character_option)}")


