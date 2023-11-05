import numpy as np
import sounddevice as sd
from scipy.signal import chirp

def sine_sweep_with_fadeout(start_freq, end_freq, duration, fadeout_duration):
    # Generate time vector
    t = np.linspace(0, duration, int(duration * 44100))

    # Generate the sweep signal
    signal = chirp(t, f0=start_freq, f1=end_freq, t1=duration, method='linear')

    # Apply a fade-out at the end of the sweep
    fadeout_samples = int(fadeout_duration * 44100)
    fadeout_window = np.linspace(1, 0, fadeout_samples)
    signal[-fadeout_samples:] *= fadeout_window

    # Normalize to 16-bit range and convert to 16-bit data
    signal = np.int16(signal / np.max(np.abs(signal)) * 32767)

    return signal

# Constants for the sweep
start_freq = 61  # Starting frequency in Hz (approximately B1)
end_freq = 37    # Ending frequency in Hz (approximately D1)
duration = 10    # Duration of the sweep in seconds
fadeout_duration = 0.5  # Duration of the fade-out in seconds

# Generate the sine sweep with fade-out
signal = sine_sweep_with_fadeout(start_freq, end_freq, duration, fadeout_duration)

# Play the sound
sd.play(signal, 44100)

# Wait for the sound to finish
sd.wait()

# Properly close the stream
sd.stop()
