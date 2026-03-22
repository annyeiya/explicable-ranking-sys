import numpy as np
import faiss
from pathlib import Path
from typing import Optional
from typing import TYPE_CHECKING

from app.core.logger import get_logger
from app.infrastructure.data.embedding import EmbeddingManager
from app.infrastructure.data.faiss_index import FaissIndexManager
from app.infrastructure.data.kb_loader import KnowledgeBaseLoader

if TYPE_CHECKING:
    from app.services.encoder import Encoder

logger = get_logger("kb")


class KnowledgeBase:
    """Основной класс для работы с базой знаний"""

    def __init__(self, encoder: 'Encoder', base_dir: Path, file_name: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.loader = KnowledgeBaseLoader(self.base_dir / file_name)
        self.embedding_manager = EmbeddingManager(encoder, self.base_dir)
        self.index_manager = FaissIndexManager(self.base_dir)

        self._entries: list[dict] = []
        self._vectors: Optional[np.ndarray] = None
        self._org_means: Optional[dict[str, np.ndarray]] = None
        self._faiss_index: Optional[faiss.Index] = None

        self._load_all()

    def _load_all(self):
        """Загружает все компоненты"""
        self._entries = self.loader.load_entries()

        if not self._entries:
            logger.warning("База знаний пуста!")
            return

        texts = [e["function"] for e in self._entries]
        self._vectors = self.embedding_manager.compute_or_load_vecs(texts)

        self._load_org_means()

        self._load_faiss_index()

    def _load_org_means(self):
        """Загружает средние эмбеддинги органов"""
        means_path = self.base_dir / "org_means.npy"

        if means_path.exists():
            logger.info(f"Загрузка средних эмбеддингов органов из {means_path}")
            self._org_means = np.load(means_path, allow_pickle=True).item()
        else:
            logger.info("Вычисление средних эмбеддингов органов...")
            orgs = self.loader.get_orgs(self._entries)
            self._org_means = self.embedding_manager.compute_org_means(self._entries, orgs)
            np.save(means_path, np.array(self._org_means, dtype=object), allow_pickle=True)

    def _load_faiss_index(self):
        """Загружает или строит FAISS индекс"""
        self._faiss_index = self.index_manager.load_index()

        if self._faiss_index is None and self._vectors is not None:
            logger.info("Построение FAISS индекса...")
            self._faiss_index = self.index_manager.build_index(self._vectors)
            self.index_manager.save_index(self._faiss_index)

    def recompute(self):
        """
        Пересчитывает все эмбеддинги и индексы.
        """
        logger.info("Пересчет всех эмбеддингов и индексов...")

        texts = [e["function"] for e in self._entries]
        self._vectors = np.array(self.embedding_manager.encoder.encode(texts))

        vecs_path = self.base_dir / "kb_vecs.npy"
        np.save(vecs_path, self._vectors)
        logger.info(f"Эмбеддинги функций сохранены: {vecs_path}")

        orgs = self.loader.get_orgs(self._entries)
        self._org_means = self.embedding_manager.compute_org_means(self._entries, orgs)

        means_path = self.base_dir / "org_means.npy"
        np.save(means_path, np.array(self._org_means, dtype=object), allow_pickle=True)
        logger.info(f"Средние эмбеддинги органов сохранены: {means_path}")

        # Перестраиваем FAISS индекс
        self._faiss_index = self.index_manager.build_index(self._vectors)
        self.index_manager.save_index(self._faiss_index)
        logger.info(f"FAISS индекс перестроен")

    @property
    def entries(self) -> list[dict]:
        return self._entries

    @property
    def vectors(self) -> np.ndarray:
        return self._vectors

    @property
    def org_means(self) -> dict[str, np.ndarray]:
        return self._org_means

    @property
    def faiss_index(self) -> faiss.Index:
        return self._faiss_index

    @property
    def size(self) -> int:
        return len(self._entries)
