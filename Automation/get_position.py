import pyautogui
import time

print("Move your mouse to the desired position... (you have 5 seconds)")
time.sleep(5)

x, y = pyautogui.position()
print(f"Mouse position is: x={x}, y={y}")