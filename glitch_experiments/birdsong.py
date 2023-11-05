import os
import subprocess

# Function to run shell commands
def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print("Error:", stderr.decode())
    else:
        print(stdout.decode())

# Generate a sample of noise from the audio of the file
run_command('ffmpeg -i bird-test.wav -acodec pcm_s16le -ar 128k -vn -ss 00:00:00.0 -t 00:00:01.0 noiseaud.wav')

# Generate a noise profile in sox
run_command('sox noiseaud.wav -n noiseprof noise.prof')

# Replace {Static_Reduce} with an actual value for noise reduction (e.g., 0.21)
static_reduce = "0.21"  # Adjust the noise reduction level as needed

# Clean the noise samples from the audio stream
run_command(f'sox cc-raw.wav cc.wav noisered noise.prof {static_reduce}')

# The blackbird.pl script needs to be present and executable
# The original script likely converts audio to a format resembling bird song
# This command assumes that blackbird.pl is in the current directory and executable
run_command('perl blackbird.pl -n')

# Normalize the resulting bird song audio
run_command('ffmpeg-normalize birdsong1.wav -o birdsong2.wav')

