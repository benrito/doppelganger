import numpy as np
import pyaudio
from scipy.signal import butter, lfilter
import threading

# Function to create a Butterworth low-pass filter
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

# Function to apply the low-pass filter
def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

# Function to generate ocean sound
def generate_ocean_sound(duration, fs, cutoff=1000):
    samples = np.random.normal(0, 1, size=fs*duration)
    samples = samples.astype(np.float32)
    filtered_samples = lowpass_filter(samples, cutoff=cutoff, fs=fs, order=4)
    return (filtered_samples / np.max(np.abs(filtered_samples)) * 32767).astype(np.int16)

# Function to continuously play sound
def play_sound_continuous(fs, stream, stop_event):
    duration = 1  # Generate 1 second chunks
    while not stop_event.is_set():
        ocean_chunk = generate_ocean_sound(duration, fs)
        stream.write(ocean_chunk.tobytes())

# Initialize PyAudio
p = pyaudio.PyAudio()

# Open stream
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                output=True)

# Create a stop event
stop_event = threading.Event()

# Start playback thread
playback_thread = threading.Thread(target=play_sound_continuous, args=(44100, stream, stop_event))
playback_thread.start()

# Wait for user input to stop
input("Press Enter to stop playback.\n")

# Set the stop event and wait for the thread to finish
stop_event.set()
playback_thread.join()

# Close the stream and PyAudio
stream.stop_stream()
stream.close()
p.terminate()
