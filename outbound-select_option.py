import re
import pyautogui
import pygetwindow as gw
from pathlib import Path
import time
import os


CATEGORIES = {
    "Connected": 1,
    "Left a Message": 2,
    "Not the right person / no message": 3,
    "Unfamiliar Language": 4
}

def classify_service_appointment(transcript: str) -> tuple:
    transcript = transcript.lower()

    # 1. Unfamiliar Language
    if "[unfamiliar language]" in transcript:
        label = "Unfamiliar Language"

    # 2. Not Connected Cases
    elif any(phrase in transcript for phrase in [
        "wrong number", "hung up", "voicemail full", 
        "not reachable", "background noise only", "spam", "robot call"
    ]):
        label = "Not the right person / no message"

    # 3. Left a Message
    elif any(phrase in transcript for phrase in [
        "left a message", "left a voicemail", "live message", 
        "please pass on the message", "i left my info", "left contact"
    ]):
        label = "Left a Message"

    # 4. Connected (default)
    else:
        label = "Connected"

    return CATEGORIES[label], label


def cleanup_files():
    files_to_delete = ['transcript.txt', 'audio1.mp3', 'audio1.wav']
    for file in files_to_delete:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"🗑️ Deleted: {file}")
            except Exception as e:
                print(f"❌ Could not delete {file}: {e}")
        else:
            print(f"⚠️ File not found: {file}")

def select_option_on_screen(option_number: int):
    print(f"Selecting option number: {option_number}")

    # Step 1: Find the Chrome window
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

    # Step 2: Move mouse to scrollable area and click to focus
    pyautogui.scroll(1000)

    # Step 4: Move to the first option position
    x_start, y_start = 720, 363
    pyautogui.moveTo(x_start, y_start)
    time.sleep(0.5)

    # Step 5: Navigate down to correct option
    for _ in range(option_number - 1):
        y_start += 55
        pyautogui.moveTo(x_start, y_start)
        time.sleep(0.05)

    # Step 6: Special adjustment for option 9 (Unfamiliar Language)
    if option_number == 4:
        pyautogui.moveTo(587, 624)
        pyautogui.click()
        print("Unfamiliar Language.")
        return

    pyautogui.click()
    print("✅ Option selected.")

    # Step 7: Slight scroll down to make submit button visible
    time.sleep(2.0)

    # Step 8: Click Submit button (adjust if needed)
    submit_x, submit_y = 924, 589
    pyautogui.moveTo(submit_x, submit_y)
    pyautogui.click()
    time.sleep(1.0)
    print("✅ Submit clicked.")

    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if not chrome_windows:
        print("❌ No Chrome window with 'Review' in title found.")
        return

    chrome = chrome_windows[0]
    if chrome.isMaximized:
        chrome.minimize()


with open("transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

option_number, category = classify_service_appointment(transcript)
print(f"Classification: [{option_number}] {category}")
cleanup_files()
select_option_on_screen(option_number)