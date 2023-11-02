import requests
import shutil
import subprocess
import sys
import time
import os
from typing import Iterator

# Define the Coqui API token (replace with your actual authentication token)
COQUI_API_TOKEN = 'lVSXFwuAHSwtYpDX8RLSDsAq0D6cMH5eKqC3dyj08ZhGW2befEvO5wuTPTsSLoQW'

# Define the API endpoints
voices_url = 'https://app.coqui.ai/api/v2/voices/xtts'
samples_url = 'https://app.coqui.ai/api/v2/samples/xtts/stream'

# Define the text you want to convert to speech
text_to_convert = "Hello, this is a test."

# Define the is_installed function
def is_installed(lib_name: str) -> bool:
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True

# Define the popen_ffplay function
def popen_ffplay() -> subprocess.Popen[bytes]:
    if not is_installed("ffplay"):
        message = (
            "ffplay from ffmpeg not found, necessary to play audio. "
            "On mac you can install it with 'brew install ffmpeg'. "
            "On linux and windows you can install it from https://ffmpeg.org/"
        )
        raise ValueError(message)
    args = ["ffplay", "-autoexit", "-nodisp", "-probesize", "1024", "-"]
    proc = subprocess.Popen(
        args=args,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc

# Step 1: Upload test.wav to get the voice ID
headers = {
    'accept': 'application/json',
    'Authorization': f'Bearer {COQUI_API_TOKEN}'
}

files = {
    'files': ('test.wav', open('test.wav', 'rb'))
}

response = requests.post(voices_url, headers=headers, files=files)

if response.status_code == 201:
    response_json = response.json()
    voice_id = response_json.get('voice', {}).get('id')
    if voice_id:
        print(f'Voice ID: {voice_id}')
    else:
        print('Voice ID not found in the response.')
else:
    print(f'Error uploading test.wav: {response.status_code}')

# Step 2: Use the obtained voice ID to generate text-to-speech and stream/save the audio
def stream_and_save_audio(text: str, language: str, voice_id: str, filename: str) -> None:
    start = time.perf_counter()
    res = requests.post(
        samples_url,
        json={"text": text, "language": language, "voice_id": voice_id},
        headers={"Authorization": f"Bearer {COQUI_API_TOKEN}"},
        stream=True,
    )

    if res.status_code != 201:
        print(
            f"Endpoint failed with status code {res.status_code}:",
            res.content.decode("utf-8"),
        )
        sys.exit(1)

    audio = b""

    for chunk in res.iter_content(chunk_size=None):
        if chunk:
            audio += chunk

    end = time.perf_counter()
    print(f"Time to generate audio: {end - start}s")

    # Stream the audio
    proc = popen_ffplay()
    proc.communicate(input=audio)
    proc.poll()

    # Save the audio to a file
    with open(filename, "wb") as f:
        f.write(audio)

# Call the stream_and_save_audio function
stream_and_save_audio(text_to_convert, language="en", voice_id=voice_id, filename="output.wav")
