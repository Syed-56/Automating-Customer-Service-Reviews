import pyautogui
import pygetwindow as gw
import os
import subprocess
from pathlib import Path
import time

MAX_RETRIES = 3
DOWNLOAD_TIMEOUT = 120
CHECK_INTERVAL = 1

def activate_chrome_window():
    print("Activating Chrome window with 'Review' in title...")
    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if not chrome_windows:
        print("No Chrome window with 'Review' in title found.")
        return None
    chrome = chrome_windows[0]
    if chrome.isMinimized:
        chrome.restore()
    chrome.activate()
    chrome.maximize()
    time.sleep(1)
    return chrome

def is_download_in_progress():
    DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
    return any(fname.endswith(".crdownload") for fname in os.listdir(DOWNLOAD_DIR))

def clear_partial_downloads():
    pyautogui.moveTo(1734,94, duration=0.5)
    time.sleep(0.5)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(1680,234)
    pyautogui.click()
    time.sleep(1)
    pyautogui.moveTo(1734,94, duration=0.5)
    time.sleep(0.5)
    pyautogui.click()

def scroll_and_right_click_audio(chrome):    
    if not chrome:
        print(" Chrome window not available for UI interaction.")
        return False
    try:
        chrome = gw.getActiveWindow()
        time.sleep(1.0)
        if chrome and "deepseek" in chrome.title.lower():
            print("Caution! Currently in Deepseek tab, switching back to Review tab...")
            pyautogui.hotkey('ctrl', '1')  # or 'ctrl', 'tab'
        time.sleep(1.0)
        pyautogui.hotkey('ctrl', '2')   #check if next tab is deepseek
        time.sleep(0.5)
        chrome = gw.getActiveWindow()
        time.sleep(1.0)
        if chrome and "deepseek" in chrome.title.lower():
            print("Nice! Next tab is Deepseek, switching back to Review tab...")
            pyautogui.hotkey('ctrl', '1')
        time.sleep(1.0)
        print(" Scrolling inside Chrome to reveal 'Download Audio'...")
        pyautogui.click(chrome.left + 150, chrome.top + 150)
        time.sleep(0.5)
        pyautogui.click(333,533)
        time.sleep(0.5)
        pyautogui.click(353,533)
        time.sleep(0.5)
        pyautogui.click(287,633)
        time.sleep(0.5)
        pyautogui.click(chrome.left + 150, chrome.top + 150)
        time.sleep(3)
        pyautogui.scroll(-1000)

        x = 1728
        y = 941
        pyautogui.moveTo(x, y, duration=0.5)
        print(f" Moving to ({x}, {y}) to click 'Download Audio'...")
        pyautogui.click()  # 'Open link in new tab'
        print(" Open Call Audio clicked.")
        time.sleep(2.0)

        print(" Switching to next tab (Ctrl+2)...")
        pyautogui.hotkey('ctrl', '2')
        chrome = gw.getActiveWindow()
        time.sleep(1.0)
        if chrome and "deepseek" in chrome.title.lower():
            pyautogui.hotkey('ctrl', '1')
            print(f" UI sequence error: Switched to Deepseek tab instead of Download Audio tab.")
            return False

        print("New Tab to download audio activated.")
        time.sleep(10.0)
        print(" Clicking 'Download Audio'...")
        pyautogui.moveTo(1144, 638, duration=0.5)
        pyautogui.click()

        time.sleep(2.0)
        print(" Confirming 'Download Audio'...")
        pyautogui.moveTo(1097, 566, duration=0.5)
        pyautogui.click()

        time.sleep(1.5)
        return True
    except Exception as e:
        print(f" UI sequence error: {e}")
        return False

def wait_for_download_and_move(timeout=DOWNLOAD_TIMEOUT, check_interval=CHECK_INTERVAL):
    downloads_dir = Path.home() / "Downloads"
    destination_dir = Path("D:/Automating-Humanatic")
    destination_dir.mkdir(parents=True, exist_ok=True)
    target_filename = destination_dir / "audio1.mp3"

    print(" Waiting for .mp3 download to start/finish...")
    start_time = time.time()
    downloaded_file = None

    while time.time() - start_time < timeout:
        mp3_files = sorted(downloads_dir.glob("*.mp3"),
                           key=os.path.getmtime, reverse=True)
        if mp3_files:
            latest_file = mp3_files[0]
            if not latest_file.name.endswith(".crdownload"):
                downloaded_file = latest_file
                break
        time.sleep(check_interval)

    if not downloaded_file:
        print(" No completed .mp3 file found within timeout.")
        try:
            pyautogui.hotkey('ctrl', 'f4')  # close the spawned tab
        except Exception:
            pass
        return False

    print(f" Download complete: {downloaded_file.name}")

    # Close the spawned tab before moving
    try:
        pyautogui.hotkey('ctrl', 'f4')
    except Exception:
        pass

    print(" Moving and renaming the latest .mp3 file to 'audio1.mp3'...")
    cmd = (
        f'for /f "delims=" %f in (\'dir "{downloads_dir}\\*.mp3" /b /o-d\') do '
        f'(move /y "{downloads_dir}\\%f" "{target_filename}" & goto :done)\n:done'
    )
    subprocess.call(cmd, shell=True)

    if target_filename.exists():
        print(f" File moved and renamed to: {target_filename}")
        return True
    else:
        print(" CMD move+rename failed.")
        return False
    
def newCallFromBookmark():
    time.sleep(1.0)
    pyautogui.scroll(1000)
    time.sleep(0.5)
    pyautogui.moveTo(253,165)
    time.sleep(0.5)
    pyautogui.click()
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

if __name__ == "__main__":
    chrome = activate_chrome_window()
    time.sleep(3.0)
    if not chrome:
        print(" Could not find or activate the correct Chrome window.")
        chrome = gw.getWindowsWithTitle("Chrome")[0]
        chrome.restore() if chrome.isMinimized else None
        chrome.activate()
        chrome.maximize()
        newCallFromBookmark()
    else:
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n Attempt {attempt}/{MAX_RETRIES}")
            if not scroll_and_right_click_audio(chrome):
                print(" UI step failed; retrying...")
                time.sleep(2)
                chrome = activate_chrome_window()
                continue

            if wait_for_download_and_move():
                print(" Success.")
                break
            else:
                if is_download_in_progress():
                    clear_partial_downloads()
                print(" Download not detected; retrying...")
                time.sleep(2)
                chrome = activate_chrome_window()
                newCallFromBookmark()


        else:
            print(" Failed after all retries.")
            newCallFromBookmark()
