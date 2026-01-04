import eel
import os
from src.crystal_engine import CrystalEngine

# 1. Khởi tạo Eel trỏ vào thư mục 'web'
eel.init('web')

# 2. Khởi tạo lõi AI (Engine)
engine = CrystalEngine()

@eel.expose
def request_training():
    """
    Hàm này sẽ được gọi khi bạn nhấn nút 'Bắt đầu' trên giao diện.
    """
    data_path = "./L_DATA"
    
    # Kiểm tra thư mục dữ liệu trước khi chạy
    if not os.path.exists(data_path):
        eel.update_ui("Lỗi: Không tìm thấy thư mục ./Data", 0, 0, 0)
        return

    # Định nghĩa hàm báo cáo (Callback) để gửi dữ liệu về Frontend
    def report_to_frontend(msg, percent, v_count, e_count):
        # Gửi dữ liệu qua 'ống dẫn' Eel
        eel.update_ui(msg, percent, v_count, e_count)
        
        # QUAN TRỌNG: eel.sleep giúp Python nhường quyền điều khiển 
        # cho trình duyệt để cập nhật thanh tiến trình (Progress Bar)
        eel.sleep(0.001) 

    try:
        # Bắt đầu quá trình kết tinh trong Engine
        engine.process_training(data_path, report_to_frontend)
    except Exception as e:
        eel.update_ui(f"Lỗi hệ thống: {str(e)}", 0, 0, 0)

# 3. Khởi chạy ứng dụng
# Chế độ 'chrome' hoặc 'edge' sẽ giúp giao diện trông giống ứng dụng Desktop
try:
    eel.start('index.html', size=(900, 700))
except (SystemExit, KeyboardInterrupt):
    print("Hệ thống đã dừng.")