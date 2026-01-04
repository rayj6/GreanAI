import pickle
import random
import os
import re

class GreenChat:
    def __init__(self, model_name):
        path = f"./Brain/{model_name}.pb"
        if not os.path.exists(path):
            print(f"❌ Không tìm thấy bộ não: {path}")
            return
            
        with open(path, 'rb') as f:
            # Cấu trúc: { (word1, word2): {next_word: count} }
            self.brain = pickle.load(f)
        print(f"[*] Đã nạp tri thức: {model_name}.pb")

    def _clean_input(self, text):
        text = str(text).lower().strip()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        return text.split()

    def generate_response(self, user_input, max_words=40, temperature=1.0):
        words = self._clean_input(user_input)
        if len(words) < 1: return "..."

        # Tìm trạng thái bắt đầu từ câu hỏi của người dùng
        # Ưu tiên lấy 2 từ cuối của người dùng làm 'seed'
        if len(words) >= 2:
            state = (words[-2], words[-1])
        else:
            # Nếu chỉ có 1 từ, tìm ngẫu nhiên một trạng thái trong não bắt đầu bằng từ đó
            possible_states = [s for s in self.brain.keys() if s[0] == words[-1]]
            if not possible_states:
                return "Tôi chưa học đủ để phản hồi về chủ đề này."
            state = random.choice(possible_states)

        response = []
        
        for _ in range(max_words):
            if state not in self.brain:
                break
            
            candidates = self.brain[state]
            choices = list(candidates.keys())
            weights = list(candidates.values())
            
            # Áp dụng Temperature (Độ sáng tạo)
            # < 1.0: Logic/Thực tế | > 1.0: Sáng tạo/Nói dối
            if temperature != 1.0:
                weights = [w ** (1/temperature) for w in weights]
            
            # Bốc thăm từ tiếp theo dựa trên xác suất
            next_word = random.choices(choices, weights=weights)[0]
            
            response.append(next_word)
            
            # Cập nhật trạng thái (trượt cửa sổ sang cặp từ mới)
            state = (state[1], next_word)
            
            # Dừng lại nếu AI tự kết thúc bằng dấu câu
            if next_word in ['.', '!', '?']:
                break
        
        if not response:
            return "Tôi đang suy nghĩ..."
            
        return " ".join(response).replace(' .', '.').replace(' ?', '?').replace(' !', '!')

# --- KHỞI CHẠY ---
if __name__ == "__main__":
    ai_name = input("🤖 Nhập tên bộ não (ví dụ: GreenAI): ").strip()
    chat_system = GreenChat(ai_name)
    
    print("\n" + "="*40)
    print(f"BẮT ĐẦU CHAT VỚI {ai_name.upper()}")
    print("Mẹo: Chỉnh temperature trong code để tăng độ 'nói dối'.")
    print("Gõ 'exit' để dừng.")
    print("="*40)

    while True:
        msg = input("\nBạn: ")
        if msg.lower() in ['exit', 'quit']: break
        
        # Temperature 1.2 là mức cân bằng giữa logic và sáng tạo
        res = chat_system.generate_response(msg, temperature=0.7)
        print(f"🤖 AI: {res}")