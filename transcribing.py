import os
import subprocess
from faster_whisper import WhisperModel

# === Paths ===
mp3_path = "D:/Automating-Humanitic/audio1.mp3"
wav_path = "D:/Automating-Humanitic/audio1.wav"
transcript_path = "D:/Automating-Humanitic/transcript.txt"

_model = None  # Module-level cache

def get_whisper_model():
    global _model
    if _model is None:
        print(" Loading Faster-Whisper model (first run only)...")
        _model = WhisperModel("tiny.en", compute_type="int8", device="cpu")
    return _model

# === Step 1: Convert MP3 to WAV ===
print("🎵 Converting MP3 to WAV...")
ffmpeg_cmd = [
    "ffmpeg", "-y",  # Overwrite
    "-i", mp3_path,
    "-ar", "16000",  # 16 kHz sample rate
    "-ac", "1",      # Mono
    wav_path
]
try:
    subprocess.run(ffmpeg_cmd, check=True)
    print(" Conversion complete.")
except subprocess.CalledProcessError as e:
    print(" FFmpeg conversion failed:", e)
    exit(1)

# === Step 2: Load Whisper model (use tiny.en for best speed) ===
print(" Loading Faster-Whisper model...")
model = get_whisper_model()
print(f" Model cache state: {'Loaded' if _model is not None else 'Not loaded'}")

# === Step 3: Transcribe the WAV ===
print(" Transcribing audio...")
try:
    segments, info = model.transcribe(
        wav_path,
        beam_size=1,
        vad_filter=False,
        language=None
    )
except Exception as e:
    print(f" Error during transcription: {e}")
    exit(1)

# Insert [unfamiliar language] if not English
if info.language != "en":
    print(f" Detected non-English language: {info.language}")
    with open(transcript_path, "w", encoding="utf-8") as f:
        f.write("[unfamiliar language]\n")
else:
    with open(transcript_path, "w", encoding="utf-8") as f:
        for segment in segments:
            line = segment.text.strip()
            print(line)
            f.write(line + "\n")


print(f" Transcription complete. Saved to {transcript_path}")