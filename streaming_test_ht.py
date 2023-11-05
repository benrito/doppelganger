from pyht import Client
from dotenv import load_dotenv
from pyht.client import Client
from pyht.protos import api_pb2
from pyht import TTSOptions
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

client = Client(
    user_id=os.getenv("PLAY_HT_USER_ID"),
    api_key=os.getenv("PLAY_HT_API_KEY"),
)
# Set up TTS options
options = TTSOptions(voice="s3://voice-cloning-zero-shot/d9ff78ba-d016-47f6-b0ef-dd630f59414e/female-cs/manifest.json", format=api_pb2.FORMAT_WAV)
response_text = "hello"
# Assuming `response_text` is the text you want to convert to speech
for chunk in client.tts(response_text, options):
    # Process and play the audio chunk as it's received
    audio_data = np.frombuffer(chunk, np.float16)  # Ensure the dtype matches the expected format of the audio bytes
    play_obj = sa.play_buffer(audio_data.tobytes(), 1, 2, 24000)
    play_obj.wait_done()  # Wait for the playback to finish for this chunk
