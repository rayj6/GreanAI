import numpy as np # type: ignore
import os
import re
import pickle
import time
from collections import defaultdict

class CrystalEngine:
    def __init__(self):
        # Sử dụng dictionary để truy cập O(1) nhưng tối ưu hóa bộ nhớ
        self.vertices = {} 
        self.edges = {}
        self.domain_vectors = {}
        # Pre-compile regex để đạt tốc độ tối đa
        self.clean_re = re.compile(r'[^a-z0-9\s]')
        
    def _clean_text(self, text):
        return self.clean_re.sub('', str(text).lower()).split()

    def process_training(self, data_path, progress_callback):
        if not os.path.exists(data_path):
            progress_callback("Lỗi: Không tìm thấy Data", 0, 0, 0)
            return

        all_files = [f for f in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, f))]
        total_files = len(all_files)
        
        # Local caching để tăng tốc độ truy cập trong vòng lặp (Method Inlining)
        v_ref = self.vertices
        e_ref = self.edges
        d_ref = self.domain_vectors
        
        for index, filename in enumerate(all_files):
            domain = filename.split('.')[0]
            file_path = os.path.join(data_path, filename)
            
            # Chỉ cập nhật giao diện sau khi xong 1 file để tiết kiệm tài nguyên
            progress_callback(f"Đang kết tinh: {filename}", int((index / total_files) * 100), len(v_ref), len(e_ref))
            
            if domain not in d_ref:
                # Tạo vector định hướng miền (Seed vector)
                v = np.random.uniform(-1, 1, 3)
                d_ref[domain] = v / np.linalg.norm(v)
            
            d_vec = d_ref[domain]

            try:
                # Đọc file theo chunk để chống tràn RAM nhưng vẫn đảm bảo tốc độ
                with open(file_path, 'r', encoding='iso-8859-1', errors='ignore') as f:
                    for line in f:
                        try:
                            content = line.split("+++$+++")[-1] if "+++" in line else line
                            words = self.clean_re.sub('', content.lower()).split()
                            
                            if len(words) < 2: continue
                            
                            # Thuật toán kết tinh tốc độ cao
                            for i in range(len(words) - 1):
                                w1, w2 = words[i], words[i+1]
                                
                                if w1 not in v_ref:
                                    v_ref[w1] = np.random.normal(0, 10, 3)
                                
                                if w2 not in v_ref:
                                    # Công thức phát triển tinh thể: V2 = V1 + Direction * Growth_Factor
                                    v_ref[w2] = v_ref[w1] + (d_vec * 2.5)
                                
                                # Tạo khóa cạnh nhanh bằng cách kết hợp chuỗi (nhanh hơn tuple trong một số phiên bản Python)
                                edge_id = f"{w1}<->{w2}" if w1 < w2 else f"{w2}<->{w1}"
                                
                                if edge_id not in e_ref:
                                    e_ref[edge_id] = 0.2 # Độ cứng khởi tạo
                                elif e_ref[edge_id] < 2.5:
                                    e_ref[edge_id] += 0.1
                        except:
                            continue # Bỏ qua dòng lỗi
            except:
                continue # Bỏ qua file lỗi

        self.save_all()
        progress_callback("HOÀN TẤT KẾT TINH!", 100, len(self.vertices), len(self.edges))

    def save_all(self):
        brain_dir = "./Brain"
        if not os.path.exists(brain_dir): os.makedirs(brain_dir)
        
        # Lưu nhị phân để Inference nhanh
        with open(os.path.join(brain_dir, "crystal_brain.pb"), 'wb') as f:
            pickle.dump({"vertices": self.vertices, "edges": self.edges}, f)
        
        self.export_to_obj(os.path.join(brain_dir, "knowledge_map.obj"))

    def export_to_obj(self, filename):
        """Xuất mô hình 3D với bộ đệm (buffering) cực lớn để tối ưu ổ cứng SSD"""
        if not self.vertices: return
        
        with open(filename, 'w', buffering=1024*1024*10) as f: # 10MB Buffer
            f.write("# Green AI - Advanced Crystal Geometry\n")
            
            # Map word to ID để ghi file .obj
            word_to_id = {}
            idx = 1
            
            # Viết Vertex với độ chính xác số thực tối ưu (4 chữ số thập phân)
            for word, coord in self.vertices.items():
                word_to_id[word] = idx
                f.write(f"v {coord[0]:.4f} {coord[1]:.4f} {coord[2]:.4f}\n")
                idx += 1
            
            # Viết Cạnh (Line)
            for edge_id in self.edges.keys():
                w1, w2 = edge_id.split("<->")
                if w1 in word_to_id and w2 in word_to_id:
                    f.write(f"l {word_to_id[w1]} {word_to_id[w2]}\n")