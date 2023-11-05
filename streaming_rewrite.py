from whisper_mic.whisper_mic import WhisperMic
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import threading
from threading import Lock
import time
import json
import openai
import re
from collections import defaultdict
from playsound import playsound
from pydub import AudioSegment, effects
from pydub.playback import play
from pydub.generators import Sine
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
from embodiment import get_device_with_max_channels


load_dotenv()

beep_start = 'media/beep_start.wav'
openai.api_key = os.getenv("OPENAI")
eleven_labs_api_key = os.getenv("ELEVEN")

# Initialize the session
whisper_mic = WhisperMic()

def send_to_eleven_labs_api(text, timestamp):
    voice = "https://api.elevenlabs.io/v1/text-to-speech/o7lPjDgzlF8ZloHzVPeK"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_labs_api_key
    }

    response = requests.post(voice, json={"text": text, "voice_settings": {"stability": 0, "similarity_boost": 0}}, headers=headers)
    if response.status_code == 200:
        filename = f"working/{timestamp}_response{len(os.listdir('working')) + 1}.mp3"
        with open(filename, "wb") as f:
            f.write(response.content)
            print(f"\n\nGenerating audio for: {filename}")
        return filename
    else:
        print(f"Request to API failed with status code {response.status_code}.")
        return None

def play_audio(filename):
    data, samplerate = sf.read(filename)
    sd.play(data, samplerate)
    sd.wait()

while True:
    timestamp = str(int(time.time()))
    print(timestamp)
    playsound(beep_start)
    print("Say something!")

    utterance = whisper_mic.listen()
    print(f"You said: {utterance}")

    with open(f"working/{timestamp}_recording.txt", "w") as f:
        f.write(utterance)

    # Generate responses using OpenAI
    model_id = "gpt-3.5-turbo-instruct"
    max_tokens = 1024
    prompt = f"You are my subconscious. Echo back my subliminal thoughts in three one-liners:\n\n'{utterance}.'\n\nRespond with a simple JSON array, correctly formatted strings:"
    
    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=max_tokens
    )

    responses = json.loads(response.choices[0].text.strip())
    
    filename = f"working/{timestamp}_responses.json"
    with open(filename, "w") as f:
        json.dump(responses, f)

    # Convert the generated responses to audio using Eleven Labs API
    files_to_play = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(send_to_eleven_labs_api, text, timestamp) for text in responses]
        for future in as_completed(futures):
            result = future.result()
            if result:
                files_to_play.append(result)

    # Playback all files sequentially
    for filename in files_to_play:
        play_audio(filename)

    print("All tasks completed, ready for next iteration.")
    time.sleep(1)  # Optional: Add a pause before the next loop starts
