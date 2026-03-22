import os

import numpy as np
from sentence_transformers import SentenceTransformer
from safetensors.torch import load_file

from app.core.logger import get_logger
from app.core.state import State
from app.infrastructure.ml import model

logger = get_logger("encoder")


class Encoder:
    """Класс векторизации текста"""

    def __init__(self, model_file: str):
        self.model_file = model_file

        if not os.path.exists(model_file):
            logger.error(f"Файл модели не найден: {model_file}")
            raise FileNotFoundError(f"Файл модели не найден: {model_file}")

        logger.info(f"Загружаем модель...")

        if State.torch_model:
            self.encoder = self._loader()
        else:
            self.model = SentenceTransformer(self.model_file)

        logger.info(f"Загружена модель {model_file}")

    def encode(self, sentence: list[str]) -> np.ndarray:
        """
        Векторизует заданные фразы.
        :param sentence: Список фраз для векторизации.
        :return: Numpy векторы.
        """
        if State.torch_model:
            return self.encoder.encode(sentence)
        else:
            emb = self.model.encode(sentence, normalize_embeddings=True)
            return np.array(emb).astype("float32")

    def _loader(self):
        encoder = model.encoder
        state_dict = load_file(self.model_file)
        encoder.load_state_dict(state_dict)
        encoder.eval()
        return encoder
