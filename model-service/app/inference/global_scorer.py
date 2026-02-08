import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class GlobalScorer:
    def __init__(self, encoder, kb, compressor):
        self.encoder = encoder
        self.kb = kb
        self.compressor = compressor

        self.org_mean_vectors = kb.org_mean_vecs

    def get_context_scores(self, text, top_n=3):
        summary = self.compressor.summarize_text(text)
        print(f"саммари текста: {summary}")
        summary_vec = np.array(self.encoder.encode([summary]))[0]

        orgs = list(self.org_mean_vectors.keys())
        vecs = np.array([self.org_mean_vectors[o] for o in orgs])
        sims = cosine_similarity([summary_vec], vecs)[0]

        # ranked = sorted(zip(orgs, sims), key=lambda x: x[1], reverse=True)
        return {org: round(float(sim), 3) for org, sim in zip(orgs, sims)}
