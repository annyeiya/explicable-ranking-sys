import numpy as np
from pathlib import Path

from app.core.logger import get_logger

logger = get_logger("kb")


class EmbeddingManager:
    """Управляет эмбеддингами и их кэшированием"""

    def __init__(self, encoder, cache_dir: Path):
        self.encoder = encoder
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def compute_or_load_vecs(self, texts: list[str], cache_name: str = "kb_vecs") -> np.ndarray:
        """
        Вычисляет или загружает эмбеддинги текстов.
        :param texts: Список из объединенных функций органов.
        :param cache_name: Имя файла для хранения эмбеддингов.
        :return: Средние эмбеддинги органов.
        """
        cache_path = self.cache_dir / f"{cache_name}.npy"

        if cache_path.exists():
            logger.info(f"Загрузка эмбеддингов из {cache_path}")
            return np.load(cache_path, allow_pickle=True)

        logger.info(f"Вычисление эмбеддингов ({len(texts)} текстов)...")
        vecs = np.array(self.encoder.encode(texts))
        np.save(cache_path, vecs)
        return vecs

    def compute_org_means(self, entries: list[dict], orgs: list[str]) -> dict[str, np.ndarray]:
        """
        Вычисляет средние эмбеддинги для органов.
        :param entries: Список записей в базе знаний.
        :param orgs: Список органов.
        :return: Средние эмбеддинги для органов.
        """
        org_means = {}
        for org in orgs:
            funcs = [e["function"] for e in entries if e["org"] == org]
            if funcs:
                vecs = np.array(self.encoder.encode(funcs))
                org_means[org] = vecs.mean(axis=0)
        return org_means
