import subprocess
import time
import os
import requests
import keyboard 
import pygetwindow as gw
import pyautogui

MAX_CALLS = 1
call_count = 0

def is_connected():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except requests.ConnectionError:
        return False


def run_script(script_name):
    print(f"\n▶️ Running: {script_name}")
    result = subprocess.run(["python", script_name])
    if result.returncode != 0:
        print(f"❌ Error running {script_name}")
        return False
    return True

def wait_for_file_completion(file_path, min_size=100, timeout=20):
    waited = 0
    while waited < timeout:
        if os.path.exists(file_path) and os.path.getsize(file_path) > min_size:
            return True
        time.sleep(0.5)
        waited += 0.5
    print(f"⚠️ Timeout: File {file_path} did not reach expected size.")
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
        print("❌ No Chrome window with 'Review' in title found.")
        return

    chrome = chrome_windows[0]
    if chrome.isMinimized:
        chrome.restore()
    chrome.activate()
    chrome.maximize()
    time.sleep(1.5)

    # Move and click Main Menu or any UI control
    pyautogui.moveTo(205, 114)
    pyautogui.scroll(1000)
    pyautogui.click()
    print("🏠 Returned to Main Menu.")

def main_loop():
    global call_count

    while call_count < MAX_CALLS:
        if keyboard.is_pressed('esc'):
            print("\n⏹️ ESC pressed. Stopping the loop.")
            break

        if not is_connected():
            print("📡 No internet connection. Exiting.")
            break

        success1 = run_script("download_audio.py")
        if not success1:
            break
        time.sleep(1)

        success2 = run_script("transcribing.py")
        if not success2:
            break

        if not wait_for_file_completion("transcript.txt"):
            break
        time.sleep(1)

        success3 = run_script("DSV-select_option.py")
        if not success3:
            break

        call_count += 1
        print(f"✅ Completed calls: {call_count}/{MAX_CALLS}")

        classification = read_classification()
        if "Unfamiliar Language" in classification:
            print("🛑 'Unfamiliar Language' detected. Stopping the loop.")
            break

        print("🔁 Starting next call...\n")
        time.sleep(2)

    print("\n✅ Automation Finished.")
    time.sleep(5.0)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n⏹️ Stopped by user.")

return_to_main_menu()