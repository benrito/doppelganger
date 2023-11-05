from pyht import Client
from dotenv import load_dotenv
from pyht.client import Client
from pyht.protos import api_pb2
from pyht import TTSOptions
from whisper_mic.whisper_mic import WhisperMic
from dotenv import load_dotenv
import os
from playsound import playsound
import time
import openai
import requests
import json
from pydub import AudioSegment
from pydub.playback import play
import simpleaudio as sa
import numpy as np

load_dotenv()
beep_start = 'media/beep_start.wav'
openai.api_key = os.getenv("OPENAI")
eleven_labs_api_key = os.getenv("ELEVEN")

# Initialize the session
whisper_mic = WhisperMic()

while True:
    timestamp = str(int(time.time()))
    print(timestamp)
    playsound(beep_start)
    print("Say something!")

    # Listen for a single utterance
    utterance = whisper_mic.listen()
    print(f"You said: {utterance}")

    # Save the utterance to a file
    with open(f"working/{timestamp}_recording.txt", "w") as f:
        f.write(utterance)

    # GPT-3.5 model ID
    model_id = "gpt-3.5-turbo-instruct"
    max_tokens = 1024

    # Prepare the prompt for the GPT model
    prompt = f"You are my subconscious. Echo back my subliminal thoughts:\n\n'{utterance}'"
    
    # Get the response from OpenAI's GPT model
    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=max_tokens
    )
    
    response_text = response['choices'][0]['text'].strip()  # Using strip() to remove any leading/trailing whitespace
    print(f"Model response: {response_text}")

    client = Client(
    user_id=os.getenv("PLAY_HT_USER_ID"),
    api_key=os.getenv("PLAY_HT_API_KEY"),
    )
    # Set up TTS options
    options = TTSOptions(voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json", format=api_pb2.FORMAT_WAV)
    # Assuming `response_text` is the text you want to convert to speech
    for chunk in client.tts(response_text, options):
        # Process and play the audio chunk as it's received
        audio_data = np.frombuffer(chunk, np.float16)  # Ensure the dtype matches the expected format of the audio bytes
        play_obj = sa.play_buffer(audio_data.tobytes(), 1, 2, 24000)
        play_obj.wait_done()  # Wait for the playback to finish for this chunk
