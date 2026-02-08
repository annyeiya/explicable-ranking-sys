from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import faiss


def compute_similarities(phrase_vecs, know_vase):
    return cosine_similarity(phrase_vecs, know_vase)


class Matcher:
    def __init__(self, kb, threshold=0.4, encoder=None):
        self.kb = kb
        self.threshold = threshold
        self.encoder = encoder

        self.faiss_count = kb.size // 5

    def math(self, phrases):
        phrase_vecs = np.array(self.encoder.encode(phrases)).astype("float32")
        faiss.normalize_L2(phrase_vecs)

        results = []
        # sims = compute_similarities(phrase_vecs, self.kb.kb_vecs)
        sims, idxs = self.kb.faiss_index.search(phrase_vecs, self.faiss_count)
        idxs = idxs.astype(int)
        for i, phrase in enumerate(phrases):
            for sim, j in zip(sims[i], idxs[i]):
                if sim >= self.threshold:
                    entry = self.kb.kb_entries[j]
                    results.append({
                        "org": entry["org"],
                        "text_phrase": phrase,
                        "function": entry["function"],
                        "similarity": round(float(sim), 3)
                    })
        return results
