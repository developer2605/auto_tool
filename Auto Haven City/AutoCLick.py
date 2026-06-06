import pyautogui
import time

# --- 1. CÀI ĐẶT THÔNG SỐ Ở ĐÂY ---
TOA_DO_NUT_SUA_X = 1420  # Thay bằng tọa độ X của bạn
TOA_DO_NUT_SUA_Y = 394   # Thay bằng tọa độ Y của bạn
THOI_GIAN_CHO_TOI_DA = 60 # Số giây tối đa tool sẽ chờ bảng popup hiện lên

def auto_xoa_san_pham_toi_uu(so_lan_lap):
    print("⏳ Tool sẽ bắt đầu sau 3 giây. Vui lòng mở sẵn màn hình danh sách sản phẩm...")
    time.sleep(3) 

    for i in range(so_lan_lap):
        print(f"\n--- Đang thực hiện xóa sản phẩm thứ {i+1} ---")
        
        try:
            # BƯỚC 1: BẤM NÚT SỬA BẰNG TỌA ĐỘ
            print("1. Click nút Sửa...")
            pyautogui.click(x=TOA_DO_NUT_SUA_X, y=TOA_DO_NUT_SUA_Y)
            
            # BƯỚC 2: VÒNG LẶP WHILE CHỜ NÚT XÓA XUẤT HIỆN (THÔNG MINH)
            print(f"2. Đang chờ nút Xóa xuất hiện (tối đa {THOI_GIAN_CHO_TOI_DA} giây)...")
            thoi_gian_bat_dau = time.time()
            vi_tri_xoa = None
            
            # Vòng lặp: Chừng nào thời gian chờ chưa vượt quá mức tối đa
            while time.time() - thoi_gian_bat_dau < THOI_GIAN_CHO_TOI_DA:
                # Cố gắng quét tìm nút xóa
                vi_tri_xoa = pyautogui.locateCenterOnScreen(r'C:\Users\hungnv\Desktop\nut_xoa.png', confidence=0.8)
                
                if vi_tri_xoa:
                    # Nếu tìm thấy, thoát ngay khỏi vòng lặp while để đi tiếp
                    break
                
                # Nếu chưa thấy, nghỉ 0.5 giây rồi tìm lại (giúp máy tính không bị quá tải)
                time.sleep(1)
            
            # BƯỚC 3: XỬ LÝ KẾT QUẢ SAU KHI TÌM KIẾM
            if vi_tri_xoa:
                pyautogui.click(vi_tri_xoa)
                thoi_gian_cho = round(time.time() - thoi_gian_bat_dau, 1)
                print(f"-> Đã click nút Xóa (Mất {thoi_gian_cho} giây để tải bảng).")
                
                # Đợi một chút để Facebook xóa xong và trượt sản phẩm bên dưới lên
                # (Bạn có thể tăng/giảm thời gian này tùy tốc độ mạng)
                time.sleep(5) 
                
            else:
                print(f"-> ❌ LỖI: Đã chờ {THOI_GIAN_CHO_TOI_DA} giây nhưng nút Xóa không hiện ra.")
                # Bấm phím ESC để đóng bảng (nếu nó bị kẹt) và kết thúc để tránh lỗi lan truyền
                pyautogui.press('esc')
                time.sleep(5)
                break 

        except Exception as e:
            print(f"Có lỗi xảy ra: {e}")
            break
            
    print("\n✅ [ HOÀN THÀNH TIẾN TRÌNH ]")

# --- 2. CHẠY THỬ TOOL ---
auto_xoa_san_pham_toi_uu(575)