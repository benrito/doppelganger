def get_device_with_max_channels():
    devices = sd.query_devices()
    max_channels = 0
    max_device_id = None

    for device in devices:
        if device['max_output_channels'] > max_channels:
            max_channels = device['max_output_channels']
            max_device_id = device['index']

    if max_device_id is None:
        raise ValueError("No suitable device found.")
    
    return max_device_id

def loop():
    def detect_taps(threshold=10, tap_interval=1, taps_required=3):
        """
        Continuously monitor the microphone for taps.
        """
        tap_count = 0
        last_tap_time = time.time()

        def callback(indata, frames, pa_time, status):
            nonlocal tap_count, last_tap_time
            volume_norm = np.linalg.norm(indata) * 10
            if volume_norm > threshold:
                print("\n\nTap detected!")  # Log message for tap detection
                if time.time() - last_tap_time < tap_interval:
                    tap_count += 1
                else:
                    tap_count = 1
                last_tap_time = time.time()

        with sd.InputStream(callback=callback):
            while tap_count < taps_required:
                sd.sleep(int(tap_interval * 1000))  # sleep for tap_interval seconds

        return True

    MAX_ATTEMPTS = 3
    attempts = 0

    r = sr.Recognizer()

    while attempts < MAX_ATTEMPTS:
        # Wait for taps
        if detect_taps():
            playsound(beep_start)

        with sr.Microphone() as source:
            print("\n\nI'm listening...")
            audio = r.listen(source)
            with open(f"working/{timestamp}_recording.wav", "wb") as f:
                f.write(audio.get_wav_data())

        # Use the recognizer to convert speech to text, playing some atmospherics while we wait
        try:

            def mirror_recording():
                mirror = OtherworldlyAudio(f"working/{timestamp}_recording.wav")
                time.sleep(3)  # wait for n second
                mirror.pitch_shift()
                mirror.play_sound()

            def ambient_background(radiation, stop_event):
                while not stop_event.is_set():
                    playsound(radiation)

            # Create and start the thread
            stop_event = threading.Event()
            sound_thread = threading.Thread(target=ambient_background, args=(radiation, stop_event))
            mirror_thread = threading.Thread(target=mirror_recording)
            sound_thread.daemon = True
            sound_thread.start()

            # Recognize the speech input using Google Speech Recognition
            playsound(acknowledgement)
            mirror_thread.start()

            # TODO: add spinner
            text = r.recognize_google(audio)
            print("\n\nI heard: " + text)

            # Prepare to pass the transcript to the prompt
            revelation = text

            with open(f"working/{timestamp}_recording.txt", "w") as f:
                f.write(revelation)

            break  # Exit the loop since we successfully got the transcript

        except sr.UnknownValueError:
            print("\n\nI couldn't understand you. Tap again.")
            playsound(beep_stop)
            stop_event.set()  # Stop the radiation sound
            attempts += 1
            if attempts == MAX_ATTEMPTS:
                playsound(beep_stop)
                sys.exit(1)

        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            stop_event.set()  # Stop the radiation sound
            attempts += 1
            if attempts == MAX_ATTEMPTS:
                playsound(beep_stop)
                sys.exit(1)