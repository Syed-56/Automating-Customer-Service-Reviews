import re
import pyautogui
import pygetwindow as gw
import time
import os

VISIT_CATEGORIES = {
    "Yes, at a specific time or range of time within 1 hour": 1,
    "Yes, at a loose time or range of time exceeding 1 hour": 2,
    "No, visit requested/mentioned but no agreement": 3,
    "No, a new visit was not discussed": 4,
    "Correction: not an inventory sales conversation": 5,
    "Unfamiliar Language": 6
}

def log_case(transcript, option_number, category):
    with open("dsv_log.txt", "a", encoding="utf-8") as f:
        f.write("==== NEW TRANSCRIPT ====\n")
        f.write(f"Transcript:\n{transcript.strip()}\n")
        f.write(f"Result: [{option_number}] {category}\n\n")

def has_visit_intent(transcript: str) -> bool:
    visit_phrases = [
        "come by", "stop by", "swing by", "visit", "drop by", "pass by",
        "be there", "head over", "see you there", "i’m coming in",
        "i’ll be at the dealership", "drive over", "i’ll be in", "coming over",
        "i will drop by", "i'll be around", "i’m planning to visit", "i’ll come by",
        "headed your way", "coming in to check it out", "will stop through",
        "heading to the store", "coming in tomorrow"
    ]
    return any(phrase in transcript for phrase in visit_phrases)

def has_negation(transcript: str) -> bool:
    negation_phrases = [
        "can’t come", "won’t come", "not coming", "can’t make it", "i’m not",
        "i won’t", "i don’t think", "probably not", "don’t plan to", "not planning"
    ]
    return any(phrase in transcript for phrase in negation_phrases)

def classify_dealership_visit(transcript: str) -> tuple:
    transcript = transcript.lower()

    # Option 6 – Unfamiliar Language
    if "[unfamiliar language]" in transcript:
        return VISIT_CATEGORIES["Unfamiliar Language"], "Unfamiliar Language"

    # Option 5 – Correction
    inventory_keywords = [
        "car", "vehicle", "truck", "test drive", "inventory",
        "trade", "purchase", "buy", "sell"
    ]
    if (
        not any(kw in transcript for kw in inventory_keywords)
        and not has_visit_intent(transcript)
        and not has_negation(transcript)
    ):
        return VISIT_CATEGORIES["Correction: not an inventory sales conversation"], "Correction: not an inventory sales conversation"

    # Specific and loose time
    specific_time_patterns = [
        r"\b(in|after|within|about|around|approximately)\s?\d{1,2} (minutes?|mins?)\b",
        r"\b(30|45|60)\s?(minutes?|mins?)\b",
        r"\b(?:at|around|by|before|after)\s?\d{1,2}(:\d{2})?\s?(am|pm)?\b",
        r"\b(on my way|heading (over|your way)|be there in a few(?! hours))\b",
        r"\btomorrow (morning|evening|afternoon)?\b",
        r"\b(early|late) (afternoon|morning|evening)\b",
        r"\bat (noon|midnight)\b",
        r"\bin \d{1,2} minutes\b",
        r"\baround lunch\b"
    ]
    loose_time_phrases = [
        "sometime today", "this weekend", "this evening", "after work",
        "in a few hours", "few hours", "later today", "in the afternoon",
        "in the evening", "after lunch", "after i get off", "i’ll swing by later",
        "i’ll be there between", "i might pass by", "after dinner",
        "next few days", "in a little while", "after my shift", "after work ends",
        "later on", "sometime next week", "over the weekend"
    ]

    has_specific_time = any(re.search(p, transcript) for p in specific_time_patterns)
    has_loose_time = any(phrase in transcript for phrase in loose_time_phrases)

    # Intent phrases
    definite_intent_phrases = [
        "i'll be there", "i will come", "i’m coming", "i’m on my way",
        "i will stop by", "i’m heading there", "i’ll come", "i’m driving down",
        "coming over", "i’ll head over", "i’m visiting", "you can expect me",
        "count on me", "i’ll definitely", "i'm 100% coming", "for sure i'll be there"
    ]
    possible_intent_phrases = [
        "maybe", "i might", "i'll try", "i may", "i’m thinking about it",
        "if i get time", "i’ll see", "possibly", "we’ll see", "thinking of coming"
    ]

    has_definite_intent = any(phrase in transcript for phrase in definite_intent_phrases)
    has_possible_intent = any(phrase in transcript for phrase in possible_intent_phrases)

    # Double negation conflict handling
    if has_definite_intent and has_negation(transcript):
        return VISIT_CATEGORIES["No, visit requested/mentioned but no agreement"], "No, visit requested/mentioned but no agreement"

    # Option 1 – Specific time + definite intent + visit
    if has_specific_time and has_definite_intent and has_visit_intent(transcript):
        return VISIT_CATEGORIES["Yes, at a specific time or range of time within 1 hour"], "Yes, at a specific time or range of time within 1 hour"

    # Option 2 – Loose time + definite intent + visit
    if has_loose_time and has_definite_intent and has_visit_intent(transcript):
        return VISIT_CATEGORIES["Yes, at a loose time or range of time exceeding 1 hour"], "Yes, at a loose time or range of time exceeding 1 hour"

    # Option 3 – Visit discussed but vague intent/time
    if (
        (has_specific_time or has_loose_time) and has_possible_intent and has_visit_intent(transcript)
    ):
        return VISIT_CATEGORIES["No, visit requested/mentioned but no agreement"], "No, visit requested/mentioned but no agreement"

    if (
        has_definite_intent and has_visit_intent(transcript)
        and not (has_specific_time or has_loose_time)
    ):
        return VISIT_CATEGORIES["No, visit requested/mentioned but no agreement"], "No, visit requested/mentioned but no agreement"

    # Option 4 – Default
    if has_negation(transcript):
        return VISIT_CATEGORIES["No, a new visit was not discussed"], "No, a new visit was not discussed"

    return VISIT_CATEGORIES["No, a new visit was not discussed"], "No, a new visit was not discussed"

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

    if option_number == 6:
        pyautogui.moveTo(948, 639)
        pyautogui.click()
        print("✅ Selected: Unfamiliar Language")
        return

    pyautogui.click()
    print("✅ Option selected.")

    time.sleep(2.0)

    submit_x, submit_y = 931, 700
    pyautogui.moveTo(submit_x, submit_y)
    pyautogui.click()
    time.sleep(5.0)
    print("✅ Submit clicked.")

    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if chrome_windows:
        chrome_windows[0].minimize()

# === Main Workflow ===
with open("transcript.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

option_number, category = classify_dealership_visit(transcript)
log_case(transcript, option_number, category)
print(f"Classification: [{option_number}] {category}")
cleanup_files()
select_option_on_screen(option_number)
time.sleep(5.0)
