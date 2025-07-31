import pyautogui
import pygetwindow as gw
import os
import shutil
import subprocess
from pathlib import Path
import time


def activate_chrome_window():
    print("🧠 Activating Chrome window with 'Review' in title...")
    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if not chrome_windows:
        print("❌ No Chrome window with 'Review' in title found.")
        return None
    chrome = chrome_windows[0]
    if chrome.isMinimized:
        chrome.restore()
    chrome.activate()
    chrome.maximize()
    time.sleep(1)
    return chrome


def scroll_and_right_click_audio(chrome):
    print("🖱️ Scrolling inside Chrome to reveal 'Download Audio'...")

    # Focus Chrome before scrolling
    pyautogui.click(chrome.left + 100, chrome.top + 100)
    time.sleep(0.5)
    pyautogui.scroll(-1000)
    time.sleep(1)

    # Right-click in the **bottom-left area** of Chrome window
    x = chrome.left+5  # adjust X offset from left
    y = chrome.bottom-25  # adjust Y offset from bottom
    print(f"👉 Moving to ({x}, {y}) to right-click 'Download Audio'...")
    pyautogui.moveTo(x, y, duration=0.5)
    pyautogui.rightClick()
    print("✅ Right-clicked the audio download button.")

    time.sleep(1)
    pyautogui.click(x+50, y - 200)  # Adjust +30 if needed based on your system font size
    print("🆕 'Open link in new tab' clicked.")
    time.sleep(3.0)
    print("🧭 Simulating Ctrl+Tab to switch to newly opened tab...")
    pyautogui.hotkey('ctrl', '2')

    # Move to the download audio button and click
    time.sleep(5.0)
    print("🎯 Moving to 'Download Audio' button...")
    pyautogui.moveTo(807, 461, duration=0.5)
    pyautogui.click()
    print("💾 'Download Audio' clicked.")

    #Click download audio
    time.sleep(3.0)
    print("🎯 Moving to 'Download Audio' button...")
    pyautogui.moveTo(778, 398, duration=0.5)
    pyautogui.click()
    print("💾 ' Audio Downloaded' .")
    time.sleep(2.0)

def wait_for_download_and_move():
    downloads_dir = Path.home() / "Downloads"
    destination_dir = Path("D:/Automating-Humanitic")
    target_filename = destination_dir / "audio1.mp3"

    print("⏳ Waiting 3 seconds for download to complete...")
    time.sleep(10)
    pyautogui.hotkey('ctrl', 'f4')
    chrome_windows = [w for w in gw.getWindowsWithTitle("Review") if "Chrome" in w.title]
    if not chrome_windows:
        print("❌ No Chrome window with 'Review' in title found.")
        return

    chrome = chrome_windows[0]
    if chrome.isMaximized:
        chrome.minimize()

    print("🚚 Moving and renaming the latest .mp3 file to 'audio1.mp3'...")

    cmd = (
        f'for /f "delims=" %f in (\'dir "{downloads_dir}\\*.mp3" /b /o-d\') do '
        f'(move "{downloads_dir}\\%f" "{target_filename}" & goto :done)\n:done'
    )

    result = subprocess.call(cmd, shell=True)
    if result == 0:
        print(f"✅ File moved and renamed to: {target_filename}")
    else:
        print("❌ CMD move+rename failed.")




if __name__ == "__main__":
    chrome = activate_chrome_window()
    if chrome:
        scroll_and_right_click_audio(chrome)
        wait_for_download_and_move()
    else:
        print("❌ Could not find or activate the correct Chrome window.")
