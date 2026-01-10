import subprocess
import time
import os
import requests
import keyboard 
import pygetwindow as gw
import pyautogui
from faster_whisper import WhisperModel

MAX_CALLS = 200
call_count = 0

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False

_model = None  # Module-level cache

def get_whisper_model():
    global _model
    if _model is None:
        print(" Loading Faster-Whisper model (first run only)...")
        _model = WhisperModel("tiny.en", compute_type="int8", device="cpu")
    return _model

def transcribe_audio(model):
    # === Paths ===
    mp3_path = "C:/Automating-Humanatic/audio1.mp3"
    wav_path = "C:/Automating-Humanatic/audio1.wav"
    transcript_path = "C:/Automating-Humanatic/transcript.txt"

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
    return True

def run_script(script_name):
    print(f"\n Running: {script_name}")
    result = subprocess.run(["python", script_name])
    if result.returncode != 0:
        print(f" Error running {script_name}")
        return False
    return True

def wait_for_file_completion(file_path, min_size=10, timeout=60):
    waited = 0
    while waited < timeout:
        if os.path.exists(file_path) and os.path.getsize(file_path) > min_size:
            return True
        time.sleep(0.5)
        waited += 0.5
    print(f" Timeout: File {file_path} did not reach expected size.")
    return False

def read_classification():
    try:
        with open("classification_result.txt", "r") as f:
            result = f.read().strip()
        return result
    except FileNotFoundError:
        return ""

def return_to_main_menu():
    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if not chrome_windows:
        print(" No Chrome window with 'Review' in title found.")
        return

    chrome = chrome_windows[0]
    if chrome.isMinimized:
        chrome.restore()
    chrome.activate()
    chrome.maximize()
    time.sleep(1.5)

    # Move and click Main Menu or any UI control
    pyautogui.moveTo(259, 166)
    pyautogui.scroll(1000)
    time.sleep(2.0)
    pyautogui.click()
    print(" Returned to Main Menu.")

def main_loop(model):
    global call_count

    while call_count < MAX_CALLS:
        if keyboard.is_pressed('esc'):
            print("\n ESC pressed. Stopping the loop.")
            break

        if not is_connected():
            print(" No internet connection. Exiting.")
            break

        success1 = run_script("download_audio.py")
        if not success1:
            break
        time.sleep(1)

        success2 = transcribe_audio(model)
        if not success2:
            break

        if not wait_for_file_completion("transcript.txt"):
            break
        time.sleep(1)

        success3 = run_script("DSV-select_option.py")
        if not success3:
            break

        call_count += 1
        print(f" Completed calls: {call_count}/{MAX_CALLS}")

        classification = read_classification()
        if "Unfamiliar Language" in classification:
            print(" 'Unfamiliar Language' detected. Stopping the loop.")
            break

        print(" Starting next call...\n")
        time.sleep(2)

    print("\n Automation Finished.")
    time.sleep(5.0)

if __name__ == "__main__":
    try:
        print(" Loading Faster-Whisper model...")
        model = get_whisper_model()
        print(f" Model cache state: {'Loaded' if _model is not None else 'Not loaded'}")
        main_loop(model)
    except KeyboardInterrupt:
        print("\n Stopped by user.")

return_to_main_menu()
print("\a")
