import re
import pyautogui
import pygetwindow as gw
from pathlib import Path
import time
import pyperclip
import os
import datetime

VISIT_CATEGORIES = {
    "Specific appointment or walk-in time / range within 1 hour" : 1,
    "Unscheduled walk-in or loose appointment time / range exceeding 1 hour": 2,
    "Appointment requested/mentioned but not set": 3,
    "No appointment, walk-in, or drop-off discussed": 4,
    "Upcoming scheduled appointment": 5,
    "Vehicle already in service": 6,
    "Not an appointment opportunity": 7,
    "Correction: caller never connected to a live, qualified agent": 8,
    "Unfamiliar Language": 9
}

def log_case(transcript, option_number, category):
    #Create a unique filename using timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ssb_logs/log_{timestamp}.txt"

    # Make sure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Write to the file
    with open(filename, "w", encoding="utf-8") as f:
        f.write("==== NEW TRANSCRIPT ====\n")
        f.write(f"Transcript:\n{transcript.strip()}\n")
        f.write(f"Result: [{option_number}] {category}\n\n")

def classify_dealership_visit(transcript, instructions):
    # Focus ChatGPT tab and send
    chrome_window = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if chrome_window:
        chrome = chrome_window[0]
        if chrome.isMinimized:
            chrome.restore()
        chrome.activate()
        chrome.maximize()
        time.sleep(1)
        pyautogui.hotkey("ctrl","2")
        time.sleep(2.0)
        pyautogui.moveTo(614,621)
        pyautogui.click()
        time.sleep(1.0)

    prompt = f"""You are a Humanatic QA expert.

    Instructions:
    {instructions}

    Transcript:
    \"\"\"{transcript}\"\"\"

    Select any of the options:
    {VISIT_CATEGORIES}

    Please respond with the category name only. DONT WRITE ANYTHING ELSE and only answer from given options and If there is unfamiliar language, you will write Unfamiliar Language"""
    pyperclip.copy(prompt)
    time.sleep(1.0)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1)
    pyautogui.press("enter")
    print("🧠 Prompt sent to GPT.")
    pyautogui.moveTo(575,260)
    time.sleep(10.0)
    pyautogui.click()
    pyautogui.click()
    pyautogui.click()
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "1")
    time.sleep(0.5)
    chrome.minimize()
    copied_text = pyperclip.paste()
    copied_text = next((line.strip() for line in copied_text.splitlines() if line.strip()), "")
    new_text = re.sub(r'^\d, ', '', copied_text)
    print(new_text)
    return VISIT_CATEGORIES[new_text], new_text

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

    pyautogui.scroll(1000)

    x_start, y_start = 720, 363
    pyautogui.moveTo(x_start, y_start)
    time.sleep(0.5)

    for _ in range(option_number - 1):
        y_start += 55
        pyautogui.moveTo(x_start, y_start)
        time.sleep(0.05)

    if option_number == 8:
        pyautogui.hotkey('f5')

    if option_number == 9:
        pyautogui.hotkey('f5')

    pyautogui.click()
    print("✅ Option selected.")

    time.sleep(2.0)

    submit_x, submit_y = 931, 700
    pyautogui.moveTo(submit_x, submit_y)
    pyautogui.click()
    time.sleep(5.0)
    print("✅ Submit clicked.")

    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if chrome_windows and chrome_windows[0].isMaximized:
        chrome_windows[0].minimize()

# === Load files ===
with open("instructions-ssb.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

with open("transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

# === Run classification ===
option_number, category = classify_dealership_visit(transcript, instructions)
if option_number:
    print(f"🧠 Classification: [{option_number}] {category}")
    select_option_on_screen(option_number)
    log_case(transcript, option_number, category)
    cleanup_files()
else:
    print("❌ Skipping due to invalid classification.")
     # Switch to Humanatic tab (title contains 'Review')
    review_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if review_windows:
        review_windows[0].activate()
        time.sleep(1)
        pyautogui.press("f5")  # Refresh the page
        time.sleep(5)  # Wait for page to reload
    else:
        print("⚠️ Humanatic tab not found.")
        exit()
    
    cleanup_files()

