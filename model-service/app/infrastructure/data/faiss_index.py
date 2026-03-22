import numpy as np
import faiss
from pathlib import Path
from typing import Optional

from app.core.logger import get_logger

logger = get_logger("kb")


class FaissIndexManager:
    """Управляет FAISS индексом"""

    def __init__(self, index_dir: Path):
        self.index_dir = index_dir
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def build_index(self, vectors: np.ndarray) -> faiss.Index:
        """
        Строит FAISS индекс из векторов.
        :param vectors: Векторы.
        :return: Индексы.
        """
        d = vectors.shape[1]
        index = faiss.IndexFlatIP(d)
        index.add(vectors.astype(np.float32))
        return index

    def save_index(self, index: faiss.Index, index_name: str = "kb_faiss"):
        """
        Сохраняет индекс на диск
        :param index: Индексы.
        :param index_name: Имя файла для сохранения индексов.
        """
        index_path = self.index_dir / f"{index_name}.index"
        faiss.write_index(index, str(index_path))
        logger.info(f"FAISS индекс сохранен в {index_path}")

    def load_index(self, index_name: str = "kb_faiss") -> Optional[faiss.Index]:
        """
        Загружает индекс с диска.
        :param index_name: Имя файла с индексами.
        :return: Индексы.
        """
        index_path = self.index_dir / f"{index_name}.index"
        if index_path.exists():
            logger.info(f"Загрузка FAISS индекса из {index_path}")
            return faiss.read_index(str(index_path))
        return None
