import numpy as np
import pickle
import os
import re

class CrystalInference:
    def __init__(self, brain_path):
        with open(brain_path, 'rb') as f:
            data = pickle.load(f)
            self.vertices, self.edges = data["vertices"], data["edges"]
        print(f"[*] Hệ thống sẵn sàng với {len(self.vertices)} đỉnh tri thức.")

    def _clean(self, text):
        return re.sub(r'[^a-z0-9\s]', '', str(text).lower()).split()

    def vibrate(self, input_text, steps=12):
        words = self._clean(input_text)
        if not words: return "..."
        
        current_word = words[-1]
        response = []
        # 'history' giúp ngăn AI quay lại các từ vừa nói (Chống lặp hi hi hi)
        history = list(words) 

        for _ in range(steps):
            if current_word not in self.vertices: break
            
            candidates = []
            for (w1, w2), attr in self.edges.items():
                if current_word in (w1, w2):
                    next_w = w2 if w1 == current_word else w1
                    
                    # LUẬT MA SÁT: Cấm lặp lại 4 từ gần nhất
                    if next_w in history[-4:]: continue 
                    
                    dist = np.linalg.norm(self.vertices[w1] - self.vertices[w2])
                    # Rung động tỷ lệ thuận với độ cứng và tỷ lệ nghịch với khoảng cách
                    vibration = attr["rigidity"] / (dist + 1e-6)
                    candidates.append((next_w, vibration))
            
            if not candidates: break
            
            # Chọn đỉnh có rung động mạnh nhất
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_next = candidates[0][0]
            
            response.append(best_next)
            history.append(best_next)
            current_word = best_next
                
        return " ".join(response)

if __name__ == "__main__":
    path = "./Brain/crystal_brain.pb"
    if os.path.exists(path):
        engine = CrystalInference(path)
        while True:
            inp = input("\nBạn: ")
            if inp.lower() in ['exit', 'quit']: break
            print(f"AI (Crystal): {engine.vibrate(inp)}")