from whisper_mic.whisper_mic import WhisperMic
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import threading
from threading import Lock
import time
import json
import openai
import requests
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
openai.api_key = os.environ.get("OPENAI")
eleven_labs_api_key = os.environ.get("ELEVEN")

# Initialize the session
whisper_mic = WhisperMic()

# Start the process
while True:
    timestamp = str(int(time.time()))
    print(timestamp)
    playsound(beep_start)
    print("Say something!")
    # Listen for a single utterance
    utterance = whisper_mic.listen()
    print(f"You said: {utterance}")

    with open(f"working/{timestamp}_recording.txt", "w") as f:
        f.write(utterance)

    ########################################################################################
    ########  Utterance — prompt  ########
    ########################################################################################

    # The GPT-3.5 model ID you want to use
    model_id = "gpt-3.5-turbo-instruct"

    # The maximum number of tokens to generate in the response
    max_tokens = 1024

    # Come up with responses
    prompt = f"You are my subsconscious. Echo back my subliminal thoughts in three one-liners:\n\n'{utterance}.'\n\nRespond with a simple JSON array, correctly formatted strings:"
    # print("Prompt:\n\n"prompt)
    response = openai.Completion.create(
        engine=model_id,
        prompt=prompt,
        max_tokens=max_tokens
    )

    # Save the responses to a local file with an epoch timestamp
    filename = f"working/{timestamp}_responses.json"
    with open(filename, "w") as f:
        f.write(response.choices[0].text)
    responses = response.choices[0].text
    print("\n\nResponses:" + responses)

    ########################################################################################
    ########  Audio response — generation  ########
    ########################################################################################

    voice = "https://api.elevenlabs.io/v1/text-to-speech/o7lPjDgzlF8ZloHzVPeK"
    eleven_labs_api_key = "7392d8c1aed03a77decf691927128ba3"  # replace with your API key

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_labs_api_key
    }

    lock = Lock()

    def send_to_eleven_labs_api(text):
        global counter
        
        # Send the responses to Eleven Labs API
        response = requests.post(voice, json={"text": text, "voice_settings": {"stability": 0, "similarity_boost": 0}}, headers=headers)
        if response.status_code == 200:
            with lock:  # Acquire lock before accessing counter
                filename = f"working/{timestamp}_response{counter}.mp3"
                counter += 1  # Safely increment counter
            with open(filename, "wb") as f:
                f.write(response.content)
                print(f"\n\nGenerating audio for: {filename}")
            return filename
        else:
            print(f"Request to API failed with status code {response.status_code}.")
            return None


    def batch():
        global counter
        counter = 0  # Resetting the counter to 0 at the beginning of main
        print(f"working/{timestamp}_responses.json")
        with open(f"working/{timestamp}_responses.json", "r") as file:
            texts = json.load(file)

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(send_to_eleven_labs_api, text) for text in texts}

    batch()

    ########################################################################################
    ########  Audio response — playback  ########
    ########################################################################################

    def route_sound(filename, device_id, channel):
        # Load audio file using pydub
        sound = AudioSegment.from_file(filename, format="mp3")

        # Convert sound to numpy array and normalize
        samples = np.array(sound.get_array_of_samples()).astype(np.float32) / (2**15)
        
        max_output_channels = sd.query_devices(device_id)['max_output_channels']

        if channel >= max_output_channels:
            raise ValueError(f"The device only has {max_output_channels} output channel(s).")

        # Create an empty array with the correct number of output channels
        zeros = np.zeros((len(samples), max_output_channels), dtype=np.float32)

        # Copy the mono audio data to the desired channel
        zeros[:, channel] = samples

        # Start a stream and play it
        print(f"\n\nRouting {filename} to device {device_id} on channel {channel}")
        with sd.OutputStream(device=device_id, channels=max_output_channels, samplerate=sound.frame_rate) as stream:
            stream.write(zeros)

    def list_files_with_same_timestamp(directory):
        # List all files in the directory
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        
        # Use regex to extract timestamp and counter from filenames
        pattern = rf"(\d+)_response(\d+).mp3"

        # Group files by timestamp
        timestamp_files = defaultdict(list)
        for file in files:
            match = re.match(pattern, file)
            if match:
                timestamp, counter = match.groups()
                timestamp_files[timestamp].append((int(counter), file))

        return timestamp_files

    def showtime():
        time.sleep(1)
        directory = "working/"
        timestamp_files = list_files_with_same_timestamp(directory)

        if timestamp not in timestamp_files:
            print(f"No files with timestamp {timestamp} found.")
            return

        sorted_files = sorted(timestamp_files[timestamp], key=lambda x: x[0])

        for _, filename in sorted_files:
            filepath = os.path.join(directory, filename)
            data, samplerate = sf.read(filepath)
            sd.play(data, 24000)
            sd.wait()
            time.sleep(.25)

        print("Tap again...")

    showtime()

# Wait for an event to restart the loop...
