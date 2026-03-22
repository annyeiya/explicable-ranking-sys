from collections import defaultdict
from typing import Any
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.state import State


class Matcher:
    """Класс постобработки: сопоставление, контекстный бонус, ранжирование"""

    @staticmethod
    def match(phrases: list[str],
              sims: np.ndarray,
              index: np.ndarray,
              kb_entries: list[dict]
              ) -> list[dict[str, Any]]:
        """
        Сопоставляет фразы с записями в базе знаний по векторной близости,
        у которых схожесть превышает порог State.threshold.
        :param phrases: Список фраз.
        :param sims: Матрица схожести от FAISS индекса.
        :param index: Матрица индексов совпадений.
        :param kb_entries: Список записей в базе знаний.
        :return: Список найденных совпадений.
            Каждый элемент содержит:
                - org: название организации
                - text_phrase: исходная текстовая фраза
                - function: текст функции из базы знаний
                - similarity: числовая оценка схожести (0-1)
        """
        results = []

        for i, phrase in enumerate(phrases):
            for sim, j in zip(sims[i], index[i]):
                if sim >= State.threshold:
                    entry = kb_entries[j]
                    results.append({
                        "org": entry["org"],
                        "text_phrase": phrase,
                        "function": entry["function"],
                        "similarity": round(float(sim), 3)
                    })
        return results

    @staticmethod
    def context_score(text_vecs: np.ndarray,
                      orgs: list[str],
                      org_vec: np.ndarray
                      ) -> dict[str, float]:
        """
        Вычисляет контекстные веса для организаций на основе близости к тексту.
        :param text_vecs: Вектор всего текста после фильтрации.
        :param orgs: Список всех органов.
        :param org_vec: Список средних эмбеддингов функций органов.
        :return: Контекстный бонус для каждого органа.
        """
        sims = cosine_similarity([text_vecs], org_vec)[0]

        ranked = sorted(
            zip(orgs, sims),
            key=lambda x: x[1],
            reverse=True
        )

        boost_weights = {}

        for i, (org, _) in enumerate(ranked):
            if i == 0:
                boost_weights[org] = 0.3
            elif i == 1:
                boost_weights[org] = 0.2
            elif i == 2:
                boost_weights[org] = 0.1
            else:
                boost_weights[org] = 0.0

        return boost_weights

    @staticmethod
    def aggregate(raw_results: list[dict[str, Any]],
                  context_scores: dict[str, float]
                  ) -> list[dict[str, Any]]:
        """
        Агрегирует сырые результаты в итоговый ранжированный список организаций.
        :param raw_results: Соотнесенные пары предложений и полномочий.
        :param context_scores: Контекстный бонус каждого органа.
        :return: Финальный ранжированный топ органов.
         Каждый элемент содержит:
                - org: название организации
                - totalScore: итоговый скор (с учетом контекста)
                - matchedPhrases: список совпавших фраз с функциями
        """
        # группируем по фразам
        by_phrase = defaultdict(list)
        for item in raw_results:
            by_phrase[item["text_phrase"]].append(item)

        # topK функций на фразу
        top_func_per_phrase = []
        for phrase, items in by_phrase.items():
            sorted_items = sorted(
                items,
                key=lambda x: x["similarity"],
                reverse=True
            )[:State.top_k_func]

            top_func_per_phrase.extend(sorted_items)

        # группируем по органу
        by_org = defaultdict(list)
        for item in top_func_per_phrase:
            by_org[item["org"]].append(item)

        aggregated = []

        for org, items in by_org.items():
            similarities = [i["similarity"] for i in items]

            mean_sim = np.mean(similarities)
            base_score = mean_sim * 0.7 + len(items) * 0.3

            matches = []
            for item in items:
                matches.append({
                    "function": item["function"],
                    "similarity": item["similarity"],
                    "textPhrase": item["text_phrase"]
                })

            aggregated.append({
                "org": org,
                "base_score": round(float(base_score), 3),
                "matchedPhrases": sorted(
                    matches,
                    key=lambda x: x["similarity"],
                    reverse=True
                )
            })

        for item in aggregated:
            boost = context_scores.get(item["org"], 0.0)
            final_score = item["base_score"] + boost
            item["totalScore"] = round(float(final_score), 3)

            del item["base_score"]

        # финальная сортировка по количеству органов
        return sorted(
            aggregated,
            key=lambda x: x["totalScore"],
            reverse=True
        )[:State.top_k_org]
