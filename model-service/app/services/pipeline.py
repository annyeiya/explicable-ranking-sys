from typing import Any
import numpy as np
from typing import TYPE_CHECKING

from app.core.logger import get_logger

if TYPE_CHECKING:
    from app.infrastructure.data.kb import KnowledgeBase
    from app.services.encoder import Encoder
    from app.services.filtration import Filtration
    from app.services.matcher import Matcher

logger = get_logger("pipeline")


class Pipeline:
    def __init__(self,
                 encoder: 'Encoder',
                 matcher: type['Matcher'],
                 filtration: 'Filtration',
                 kb: 'KnowledgeBase',
                 ):
        self.encoder = encoder
        self.filtration = filtration
        self.kb = kb
        self.matcher = matcher

    def run(self, text: str) -> list[Any]:
        """
        Запускает полный цикл обработки текстового запроса.
        :param text: Входной текст.
        :return: Отранжированный список результатов.
        """
        phrases, detail = self.filtration.filter(text)
        logger.debug(f"отобранные фразы: {detail}")

        phrase_vecs = self.encoder.encode(phrases).astype("float32")

        sims, index = self.kb.faiss_index.search(phrase_vecs, self.kb.size // 5)
        index = index.astype(int)
        raw = self.matcher.match(phrases, sims, index, self.kb.entries)

        summary_vec = np.array(self.encoder.encode([" ".join(phrases)]))[0]
        org_mean_vectors = self.kb.org_means
        orgs = list(org_mean_vectors.keys())
        vecs = np.array([org_mean_vectors[o] for o in orgs])
        context_boost = self.matcher.context_score(summary_vec, orgs, vecs)

        final = self.matcher.aggregate(raw, context_boost)

        return final

    def kb_recompute(self):
        """
        Пересчитывает все эмбеддинги и перестраивает FAISS индекс базы знаний.
        """
        self.kb.recompute()
