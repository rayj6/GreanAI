import pandas as pd
import json
import os
import time
import difflib
import re

# Thư viện hỗ trợ PDF (cần cài đặt: pip install PyPDF2)
try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

class GreenAIFactory:
    def __init__(self):
        self.brain = {} 
        self.similarity_threshold = 0.6
        self.total_learned = 0

    def _clean_text(self, text):
        return str(text).lower().strip()

    def train_pair(self, i, o):
        """Học một cặp input - output"""
        state = self._clean_text(i)
        if not state: return
        if state not in self.brain:
            self.brain[state] = {}
        output = str(o).strip()
        self.brain[state][output] = self.brain[state].get(output, 0) + 1
        self.total_learned += 1

    def scan_folder(self, folder_path):
        """Quét và học tất cả các file trong thư mục"""
        start_time = time.perf_counter()
        print(f"[*] Đang quét thư mục: {folder_path}...")

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = file.lower().split('.')[-1]
                
                try:
                    # 1. Xử lý CSV & EXCEL & PARQUET
                    if ext in ['csv', 'xlsx', 'parquet']:
                        if ext == 'csv': df = pd.read_csv(file_path)
                        elif ext == 'xlsx': df = pd.read_excel(file_path)
                        else: df = pd.read_parquet(file_path)
                        
                        # Giả định: Cột 0 là Input, Cột 1 là Output
                        for row in df.iloc[:, :2].values:
                            if len(row) >= 2: self.train_pair(row[0], row[1])

                    # 2. Xử lý JSON & JSONL
                    elif ext in ['json', 'jsonl']:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            if ext == 'jsonl':
                                for line in f:
                                    data = json.loads(line)
                                    self.train_pair(data.get('input', ''), data.get('output', ''))
                            else:
                                data = json.load(f)
                                if isinstance(data, list):
                                    for item in data: self.train_pair(item.get('input', ''), item.get('output', ''))

                    # 3. Xử lý TXT
                    elif ext == 'txt':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if '|' in line: # Giả định định dạng: input | output
                                    parts = line.split('|')
                                    self.train_pair(parts[0], parts[1])

                    # 4. Xử lý PDF
                    elif ext == 'pdf' and PyPDF2:
                        with open(file_path, 'rb') as f:
                            reader = PyPDF2.PdfReader(f)
                            # PDF thường là văn bản thô, học theo cặp dòng (Line 1 -> Line 2)
                            lines = []
                            for page in reader.pages:
                                lines.extend(page.extract_text().split('\n'))
                            for i in range(len(lines)-1):
                                self.train_pair(lines[i], lines[i+1])

                    print(f"   [+] Đã học: {file}")
                except Exception as e:
                    print(f"   [!] Lỗi file {file}: {e}")

        return time.perf_counter() - start_time

    def _find_best_match(self, user_input):
        user_input = self._clean_text(user_input)
        all_states = list(self.brain.keys())
        matches = difflib.get_close_matches(user_input, all_states, n=1, cutoff=self.similarity_threshold)
        return matches[0] if matches else None

    def predict(self, user_input):
        state = self._clean_text(user_input)
        if state not in self.brain:
            state = self._find_best_match(user_input)
        
        if state and state in self.brain:
            results = self.brain[state]
            best_match = max(results, key=results.get)
            return best_match, state
        return "Tôi chưa được học về thông tin này.", None

# --- VẬN HÀNH ---
if __name__ == "__main__":
    factory = GreenAIFactory()
    
    # Đường dẫn thư mục dữ liệu của bạn
    data_folder = "./Data" 
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
        print(f"Hãy bỏ các file dữ liệu vào thư mục {data_folder} rồi chạy lại.")
    else:
        duration = factory.scan_folder(data_folder)
        
        print(f"\n{'='*50}")
        print(f"✅ HOÀN TẤT HUẤN LUYỆN")
        print(f"[*] Tổng mẫu học được: {factory.total_learned}")
        print(f"[*] Thời gian xử lý: {duration:.2f} giây")
        print(f"[*] Bộ nhớ sử dụng: {len(factory.brain)} nodes")
        print(f"{'='*50}\n")

        while True:
            user_msg = input("Bạn: ")
            if user_msg.lower() in ['exit', 'quit']: break
            
            reply, match = factory.predict(user_msg)
            print(f"AI (Match: {match}): {reply}\n")