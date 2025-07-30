import re
import pyautogui
import pygetwindow as gw
from pathlib import Path
import time
import os


CATEGORIES = {
    "Specific appointment or walk-in time / range within 1 hour": 1,
    "Unscheduled walk-in or loose appointment time / range exceeding 1 hour": 2,
    "Appointment requested / mentioned but not set": 3,
    "No appointment, walk-in, or drop-off discussed": 4,
    "Upcoming scheduled appointment": 5,
    "Vehicle already in service": 6,
    "No, not an appointment opportunity": 7,
    "Correction: caller never connected to a live, qualified agent": 8,
    "Unfamiliar Language": 9
}

def classify_service_appointment(transcript: str) -> tuple:
    transcript = transcript.lower()

    if re.search(r'\[unfamiliar language\]', transcript):
        label = "Unfamiliar Language"

    elif any(phrase in transcript for phrase in [
        "left on hold", "voicemail", "wrong number", 
        "left a live message", "declined to leave a message",
        "hung up during", "connection was lost"
    ]):
        label = "Correction: caller never connected to a live, qualified agent"

    elif re.search(r"\b(status|update).*(vehicle|car).*(already in service|already there|being serviced)", transcript):
        label = "Vehicle already in service"

    elif re.search(r"\b(already have|existing|scheduled).*appointment", transcript):
        label = "Upcoming scheduled appointment"

    elif re.search(r"\b(see you at|i'll be there at|put you down for|schedule you for|drop.*before.*appointment|come in now|within.*an hour)\b", transcript):
        label = "Specific appointment or walk-in time / range within 1 hour"

    elif re.search(r"\b(drop.*off.*day|before|after|anytime|sometime|between \d{1,2}(:\d{2})? and \d{1,2}(:\d{2})?)\b", transcript):
        label = "Unscheduled walk-in or loose appointment time / range exceeding 1 hour"

    elif re.search(r"\b(need to bring.*car|can i get an appointment|want.*appointment|how much.*service|price for)\b", transcript) and "schedule" not in transcript:
        label = "Appointment requested / mentioned but not set"

    elif re.search(r"\b(oil change|flush|how much|price|do you offer|do you do)\b", transcript) and "appointment" not in transcript:
        label = "No appointment, walk-in, or drop-off discussed"

    elif re.search(r"\b(body shop|collision|just checking|personal call|car wash|just talking|talk to someone)\b", transcript):
        label = "No, not an appointment opportunity"

    else:
        label = "Appointment requested / mentioned but not set"  # fallback

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
    x_start, y_start = 720, 366
    pyautogui.moveTo(x_start, y_start)
    time.sleep(0.5)

    # Step 5: Navigate down to correct option
    for _ in range(option_number - 1):
        y_start += 55
        pyautogui.moveTo(x_start, y_start)
        time.sleep(0.05)

    # Step 6: Special adjustment for option 9 (Unfamiliar Language)
    if option_number == 9:
        pyautogui.moveTo(720,366)
        pyautogui.scroll(-1000)
        pyautogui.moveTo(991, 479)
        pyautogui.click()
        print("Unfamiliar Language.")
        return

    pyautogui.click()
    print("✅ Option selected.")

    # Step 7: Slight scroll down to make submit button visible
    pyautogui.scroll(-300)
    time.sleep(0.5)

    # Step 8: Click Submit button (adjust if needed)
    submit_x, submit_y = 930, 618
    pyautogui.moveTo(submit_x, submit_y)
    pyautogui.click()
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