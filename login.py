from playwright.sync_api import sync_playwright
import time
import random
from dotenv import load_dotenv
import os

# Add human-like delay
def human_like_delay(min_delay=0.2, max_delay=0.7):
    time.sleep(random.uniform(min_delay, max_delay))

def login_to_humanatic(email, password):
    with sync_playwright() as p:
        # Set path to Chrome executable
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

        # Launch Chrome with remote debugging enabled
        browser = p.chromium.launch(
            headless=False,
            executable_path=chrome_path,
            args=[
                "--remote-debugging-port=9222",  # Needed for CDP connection
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )

        context = browser.new_context(
            permissions=["camera"],
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/115.0.0.0 Safari/537.36"
        )

        page = context.new_page()
        page.goto("https://www.humanatic.com/pages/humfun/login.cfm")
        page.wait_for_load_state("domcontentloaded")

        # Wait for username field
        page.wait_for_selector("input[name='username']", timeout=15000)

        # Type email
        page.click("input[name='username']")
        for char in email:
            page.keyboard.insert_text(char)
            human_like_delay(0.05, 0.15)

        human_like_delay()

        # Type password
        page.click("input[name='password']")
        for char in password:
            page.keyboard.insert_text(char)
            human_like_delay(0.05, 0.15)

        human_like_delay()

        # Click Login
        page.click("button.subbutton_mob")
        print("✅ Logged in. Waiting for face verification page...")

        # Wait until redirected to face verification
        page.wait_for_url("**/face_verify.cfm", timeout=20000)
        print("🧠 Reached face verification page.")

        # Pause here so obs_control.py can take over
        time.sleep(10)

        # Keep browser alive until killed manually or by main.py
        print("🟢 Browser stays open for obs_control.py to connect.")
        while True:
            time.sleep(1)

if __name__ == "__main__":
    load_dotenv(dotenv_path="credentials.env")
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    if not EMAIL or not PASSWORD:
        print("❌ Please check your .env file. Missing EMAIL or PASSWORD.")
    else:
        login_to_humanatic(EMAIL, PASSWORD)
