# # ====WHISPER LIVE ==== #

# # from whisper_live.server import TranscriptionServer
# # from whisper_live.client import TranscriptionClient 

# # server = TranscriptionServer()
# # server.run("0.0.0.0", 9090)

# # client = TranscriptionClient("0.0.0.0", "9090", is_multilingual=True, lang="en", translate=False)
# # client()

# # ====FASTER WHISPER==== #

# from faster_whisper import WhisperModel

# model_size = "large-v2"

# # # Run on GPU with FP16
# # model = WhisperModel(model_size, device="cuda", compute_type="float16")

# # # or run on GPU with INT8
# # # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

# segments, info = model.transcribe("audio.mp3", beam_size=5)
# segments, _ = model.transcribe("audio.mp3", vad_filter=True)
# segments = list(segments)  # The transcription will actually run here.

# print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# for segment in segments:
#     print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))

# ====WHISPER MIC ==== #


from whisper_mic.whisper_mic import WhisperMic

mic = WhisperMic()
result = mic.listen()
print(result)