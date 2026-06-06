import pyautogui
import time

print("Hãy di chuyển chuột vào nút Sửa. Tọa độ sẽ hiện ra sau 3 giây...")
time.sleep(10)
toa_do = pyautogui.position()
print(f"Tọa độ của bạn là: {toa_do}")