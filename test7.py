# Assuming the above class WhisperMic is already defined in the code
import os
import wave
from whisper_mic.whisper_mic import WhisperMic

class SaveTranscription(WhisperMic):
    def save_to_files(self, audio_data, transcribed_text, audio_filename, text_filename):
        # Save the transcribed text to a file
        with open(text_filename, 'w') as file:
            file.write(transcribed_text)
        
        # Save the audio data to a WAV file
        with wave.open(audio_filename, 'wb') as file:
            file.setnchannels(1)
            file.setsampwidth(2)  # Assuming 16-bit audio
            file.setframerate(16000)
            file.writeframes(audio_data)

    def listen_and_save(self, audio_filename="audio_output.wav", text_filename="transcription.txt"):
        self.logger.info("Listening... Please speak.")
        
        # Use the listen method to capture and transcribe audio
        transcribed_text = self.listen()
        
        # Get the audio data from the queue
        audio_data = self.__get_all_audio()
        
        # Save both the audio and the transcription
        self.save_to_files(audio_data, transcribed_text, audio_filename, text_filename)
        print(f"Transcribed text saved to {text_filename}")
        print(f"Audio saved to {audio_filename}")


if __name__ == '__main__':
    # Create an instance of the SaveTranscription class
    whisper_instance = SaveTranscription(save_file=True)
    
    # Use the listen_and_save method to listen for audio and save the results
    whisper_instance.listen_and_save()
