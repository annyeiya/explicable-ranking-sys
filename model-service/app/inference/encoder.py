from sentence_transformers import SentenceTransformer

class Encoder:
    def __init__(self, model_name="model"): 
        print(f"[INFO] Загружаем модель {model_name}...")
        self.model = SentenceTransformer(model_name)
        print("[INFO] Модель загружена!")

    def encode(self, phrases):
        return self.model.encode(phrases, normalize_embeddings=True)
