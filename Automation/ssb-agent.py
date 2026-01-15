import subprocess
import time
import os
import requests
import pygetwindow as gw
import pyautogui
from faster_whisper import WhisperModel

MAX_CALLS = 200
call_count = 0
incorrectAttempts = 0

_model = None  # Module-level cache

def get_whisper_model():
    global _model
    if _model is None:
        print(" Loading Faster-Whisper model (first run only)...")
        _model = WhisperModel("base.en", compute_type="int8", device="cpu")
    return _model

def transcribe_audio(model):
    # === Paths ===
    mp3_path = "D:/Data-Science-Basics/jupyterNotebook/QA-Calls-Review-Analysis/Automation/audio1.mp3"
    wav_path = "D:/Data-Science-Basics/jupyterNotebook/QA-Calls-Review-Analysis/Automation/audio1.wav"
    transcript_path = "D:/Data-Science-Basics/jupyterNotebook/QA-Calls-Review-Analysis/Automation/transcript.txt"

    FFMPEG = r"D:\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

    # === Step 1: Convert MP3 to WAV ===
    print("Converting MP3 to WAV...")
    ffmpeg_cmd = [
    FFMPEG, "-y",
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
        if os.path.exists(mp3_path):
            os.remove(mp3_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)
        return False

    # === Step 2: Load Whisper model (use tiny.en for best speed) ===
    print(" Loading Faster-Whisper model...")
    print(f" Model cache state: {'Loaded' if _model is not None else 'Not loaded'}")

    # === Step 3: Transcribe the WAV ===
    print(" Transcribing audio...")
    try:
        segments, info = model.transcribe(
            wav_path,
            beam_size=3,
            vad_filter=True,
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

def validateTabs():
    window = gw.getActiveWindow()

    if window and window.title.endswith(" - deepseek"):
        pyautogui.hotkey('ctrl', '1')  # or 'ctrl', 'tab'
        time.sleep(2.0)
        if window and window.title.endswith(" - deepseek"):
            pyautogui.hotkey('ctrl', 't')
            time.sleep(2.0)
            pyautogui.moveTo(1885,84)
            time.sleep(0.5)
            pyautogui.click()
            time.sleep(0.5)
            pyautogui.moveTo(1648,598)
            time.sleep(0.5)
            pyautogui.click()
            time.sleep(0.5)
            pyautogui.moveTo(1177,919)
            time.sleep(0.5)
            pyautogui.click()
            time.sleep(10)
            pyautogui.hotkey('ctrl', 'shift', 'pageup')
            time.sleep(0.5)

        # === No Calls Check ===
    nocallscountrefresh = 0
    while True:
        window = gw.getActiveWindow()
        if window and "No Calls" in window.title:
            if nocallscountrefresh < 300:
                print("No calls available. Refreshing...")
                time.sleep(10)
                nocallscountrefresh += 10
            else:
                print("No calls for 5 minutes. Exiting.")
                exit(1)
        else:
            break  # exit the No Calls loop if calls are available


def is_connected():
    try:
        requests.get("https://clients3.google.com/generate_204", timeout=3)
        return True
    except requests.RequestException:
        return False
    
def main_loop(model):
    global call_count
    global incorrectAttempts

    while call_count < MAX_CALLS:
        if incorrectAttempts>=3:
            print(" Too many incorrect attempts, aborting.")
            break
        validateTabs()
        if not is_connected():
            print(" No internet connection. Retrying in 5 seconds...")
            time.sleep(30)
            continue
        success1 = run_script("download_audio.py")
        if not success1:
            incorrectAttempts += 1
            break
        else:
            incorrectAttempts = 0
        time.sleep(1)

        success2 = transcribe_audio(model)
        if not success2:
            incorrectAttempts += 1
            continue
        else:
            incorrectAttempts = 0

        if not wait_for_file_completion("transcript.txt"):
            continue
        time.sleep(1)

        if not is_connected():
            print(" No internet connection. Retrying in 30 seconds...")
            time.sleep(30)
            continue
        success3 = run_script("SSB-select_option.py")
        if not success3:
            continue

        call_count += 1
        print(f" Completed calls: {call_count}/{MAX_CALLS}")
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
