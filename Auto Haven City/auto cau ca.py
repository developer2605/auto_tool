import tkinter as tk
from tkinter import messagebox
import threading
import cv2
import numpy as np
import time
import keyboard
import json
import os
from mss import mss
import win32gui
import win32con
import win32api

# ==========================================
# CẤU HÌNH CƠ BẢN
# ==========================================
VK_Q = 0x51
VK_E = 0x45
VK_5 = 0x35

COOLDOWN_ROD     = 40    
MONITOR_NUMBER   = 1
CONFIG_FILE      = "fishing_nested_config.json"
WINDOW_TITLE     = "FiveM® by Cfx.re"

# Cấu hình Ô Mục Tiêu (Vùng an toàn)
# Chỉnh sửa thông số này (pixel) cho khớp với chiều rộng ô màu xanh lá trong game
SAFE_ZONE_WIDTH  = 120   

# ==========================================
# HÀM GỬI PHÍM NGẦM (WIN32API)
# ==========================================
def get_game_hwnd():
    return win32gui.FindWindow(None, WINDOW_TITLE)

def press_key_bg(hwnd, vk_code):
    if not hwnd: return
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)
    time.sleep(0.05)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)

def key_down_bg(hwnd, vk_code):
    if not hwnd: return
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk_code, 0)

def key_up_bg(hwnd, vk_code):
    if not hwnd: return
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk_code, 0)

def release_all(hwnd):
    key_up_bg(hwnd, VK_Q)
    key_up_bg(hwnd, VK_E)

# ==========================================
# GIAO DIỆN & LOGIC CHÍNH
# ==========================================
class FishingBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Fishing Bot - Chạy Ngầm")
        self.root.geometry("350x250")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)

        self.is_paused = True
        self.is_running_thread = True
        self.auto_cycle_active = False
        self.last_rod_time = 0
        self.hwnd = None

        self.lbl_title = tk.Label(root, text="BOT CÂU CÁ FIVEM", font=("Arial", 14, "bold"))
        self.lbl_title.pack(pady=10)

        self.lbl_status = tk.Label(root, text="Trạng thái: ĐANG DỪNG", fg="red", font=("Arial", 10, "bold"))
        self.lbl_status.pack(pady=5)

        self.btn_select_roi = tk.Button(root, text="🎯 Chọn Vùng Target", width=25, command=self.select_roi)
        self.btn_select_roi.pack(pady=5)

        self.btn_start = tk.Button(root, text="▶ Bắt Đầu (ON)", width=25, bg="#4CAF50", fg="white", command=self.start_bot)
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(root, text="⏸ Tạm Dừng (OFF)", width=25, bg="#f44336", fg="white", command=self.pause_bot)
        self.btn_stop.pack(pady=5)

        self.lbl_info = tk.Label(root, text="Phím tắt Bật/Tắt: [", font=("Arial", 8, "italic"))
        self.lbl_info.pack(pady=10)

        keyboard.on_press_key('[', self.toggle_hotkey)
        keyboard.on_press_key('5', self.trigger_rod_hotkey)

        self.bot_thread = threading.Thread(target=self.bot_loop, daemon=True)
        self.bot_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def toggle_hotkey(self, event):
        if self.is_paused:
            self.start_bot()
        else:
            self.pause_bot()

    def trigger_rod_hotkey(self, event):
        if not self.is_paused:
            self.last_rod_time = time.time()
            self.auto_cycle_active = True
            print(f"*** Bắt đầu đếm ngược {COOLDOWN_ROD}s...")

    def select_roi(self):
        self.pause_bot()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, CONFIG_FILE)

        with mss() as sct:
            monitor = sct.monitors[MONITOR_NUMBER]
            full_img = np.array(sct.grab(monitor))
            img_bgr = cv2.cvtColor(full_img, cv2.COLOR_BGRA2BGR)
            
            self.root.withdraw()

            cv2.namedWindow("CHON VUNG TARGET", cv2.WINDOW_NORMAL)
            cv2.setWindowProperty("CHON VUNG TARGET", cv2.WND_PROP_TOPMOST, 1)
            r = cv2.selectROI("CHON VUNG TARGET", img_bgr, False)
            cv2.destroyAllWindows()
            
            self.root.deiconify()

            if r[2] > 0 and r[3] > 0:
                roi = {
                    "top": int(monitor["top"] + r[1]), 
                    "left": int(monitor["left"] + r[0]), 
                    "width": int(r[2]), 
                    "height": int(r[3])
                }
                try:
                    with open(config_path, 'w') as f:
                        json.dump(roi, f)
                    messagebox.showinfo("Thành công", f"Đã lưu tọa độ vào:\n{CONFIG_FILE}")
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
            else:
                messagebox.showwarning("Hủy", "Chưa chọn vùng target nào.")

    def start_bot(self):
        self.hwnd = get_game_hwnd()
        if not self.hwnd:
            messagebox.showerror("Lỗi", f"Không tìm thấy cửa sổ game:\n'{WINDOW_TITLE}'\nVui lòng mở game trước!")
            return

        self.is_paused = False
        self.lbl_status.config(text="Trạng thái: ĐANG CHẠY", fg="green")
    
    def pause_bot(self):
        self.is_paused = True
        self.auto_cycle_active = False
        if self.hwnd:
            release_all(self.hwnd)
        self.lbl_status.config(text="Trạng thái: ĐANG DỪNG", fg="red")

    def on_closing(self):
        self.is_running_thread = False
        self.pause_bot()
        self.root.destroy()

    def bot_loop(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, CONFIG_FILE)

        with mss() as sct:
            while self.is_running_thread:
                if self.is_paused:
                    time.sleep(0.1)
                    continue

                if not os.path.exists(config_path):
                    self.pause_bot()
                    print("Chưa cấu hình vùng chọn!")
                    time.sleep(1)
                    continue
                
                try:
                    with open(config_path, 'r') as f:
                        roi = json.load(f)
                except:
                    time.sleep(0.1)
                    continue

                # Xác định tâm điểm vùng quét toàn bộ thanh
                target_center_x = roi["width"] // 2 
                
                # Tính toán mốc (boundary) của "Ô Mục Tiêu" dựa trên SAFE_ZONE_WIDTH
                left_bound = target_center_x - (SAFE_ZONE_WIDTH // 2)
                right_bound = target_center_x + (SAFE_ZONE_WIDTH // 2)

                if self.auto_cycle_active:
                    if time.time() - self.last_rod_time >= COOLDOWN_ROD:
                        print(f">>> Tự động quăng cần (Phím 5)")
                        press_key_bg(self.hwnd, VK_5)
                        self.last_rod_time = time.time()

                try:
                    screenshot = np.array(sct.grab(roi))
                    frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    
                    mask = cv2.inRange(hsv, np.array([35, 100, 100]), np.array([100, 255, 255]))
                    conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    if conts:
                        c = max(conts, key=cv2.contourArea)
                        if cv2.contourArea(c) > 50:
                            bx, _, bw, _ = cv2.boundingRect(c)
                            
                            # Xác định mép trái và mép phải của thanh màu xanh dương
                            blue_left_edge = bx
                            blue_right_edge = bx + bw
                            
                            # Logic mới: Chạm mốc trái thì kéo qua phải (E), chạm mốc phải thì kéo qua trái (Q)
                            if blue_left_edge <= left_bound:
                                key_up_bg(self.hwnd, VK_Q)
                                key_down_bg(self.hwnd, VK_E)
                            elif blue_right_edge >= right_bound:
                                key_up_bg(self.hwnd, VK_E)
                                key_down_bg(self.hwnd, VK_Q)
                            else:
                                # Nằm gọn bên trong Ô Mục Tiêu -> nhả toàn bộ phím
                                release_all(self.hwnd)
                    else:
                        release_all(self.hwnd)
                except Exception as e:
                    print(f"Lỗi quét ảnh: {e}")
                
                time.sleep(0.01)

if __name__ == "__main__":
    root = tk.Tk()
    app = FishingBotGUI(root)
    root.mainloop()