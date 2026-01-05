import cv2 # type: ignore
import pickle
import numpy as np # type: ignore
from src.crystal_engine import CrystalEngine

# 1. Khởi tạo Engine để trích xuất đặc điểm
engine = CrystalEngine()

# 2. Nạp bộ não đã kết tinh
with open("../Brain/crystal_brain.pb", 'rb') as f:
    brain = pickle.load(f)
    vertices = brain['vertices']

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break
    
    # Lưu frame tạm thời để engine phân tích
    cv2.imwrite("temp_test.jpg", frame)
    
    # Engine nhìn ảnh và trả về các tags (eyes_open, face_detected, etc.)
    # Đảm bảo bạn đã cập nhật hàm _extract_image_features trong src/crystal_engine.py
    current_tags = engine._extract_image_features("temp_test.jpg") 
    
    status = "Searching..."
    for tag in current_tags:
        if tag in vertices:
            # Nếu tag nằm trong không gian 3D đã học, hiển thị nó
            status = f"State: {tag}"
            
    cv2.putText(frame, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Distraction Detector Test", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()