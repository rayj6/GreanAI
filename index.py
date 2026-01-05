import eel # type: ignore
import os
import base64
import cv2 # type: ignore
from src.crystal_engine import CrystalEngine

eel.init('web')
engine = CrystalEngine()

@eel.expose
def handle_universal_upload(filename, base64_data):
    data_path = "./L_DATA"
    if not os.path.exists(data_path): os.makedirs(data_path)
    
    try:
        # Tách phần header của Base64
        header, encoded = base64_data.split(",", 1)
        data = base64.b64decode(encoded)
        
        file_ext = os.path.splitext(filename)[1].lower()
        full_path = os.path.join(data_path, filename)
        
        if file_ext == ".txt":
            # Nếu là file nhãn, lưu dưới dạng văn bản utf-8
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(data.decode("utf-8"))
        else:
            # Nếu là ảnh (.jfif, .jpg...), lưu dưới dạng nhị phân
            with open(full_path, "wb") as f:
                f.write(data)
        
        print(f"Thành công: {filename}")
        return True
    except Exception as e:
        print(f"Lỗi upload: {e}")
        return False

@eel.expose
def save_uploaded_file(filename, content):
    data_path = "./L_DATA"
    if not os.path.exists(data_path): os.makedirs(data_path)
    try:
        with open(os.path.join(data_path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        return True # Trả về xác nhận
    except: return False

@eel.expose
def save_image_file(filename, base64_data):
    data_path = "./L_DATA"
    if not os.path.exists(data_path): os.makedirs(data_path)
    try:
        header, encoded = base64_data.split(",", 1)
        data = base64.b64decode(encoded)
        with open(os.path.join(data_path, filename), "wb") as f:
            f.write(data)
        return True # Trả về xác nhận
    except: return False

@eel.expose
def request_training():
    data_path = "./L_DATA"
    def report_to_frontend(msg, percent, v_count, e_count):
        eel.update_ui(msg, percent, v_count, e_count)
        eel.sleep(0.01)
    
    try:
        engine.process_training(data_path, report_to_frontend)
    except Exception as e:
        eel.update_ui(f"Lỗi: {str(e)}", 0, 0, 0)

eel.start('index.html', size=(900, 700))