import json
import numpy as np
from pathlib import Path
import faiss

class KnowledgeBase:
    def __init__(self, encoder,
                 kb_path="knowledge/kb.json",
                 vecs_path="knowledge/kb_vecs.npy",
                 org_means_path="knowledge/org_means.npy",
                 faiss_index_path="knowledge/kb_faiss.index"):
        self.encoder = encoder
        self.kb_path = Path(kb_path)
        self.vecs_path = Path(vecs_path)
        self.org_means_path = Path(org_means_path)
        self.faiss_path = Path(faiss_index_path)

        self.kb_entries = self._load_kb()
        self.kb_vecs = self._load_or_compute_vecs()
        self.org_mean_vecs = self._load_or_compute_org_means()
        self.faiss_index = self._load_or_build_faiss()

    def _load_kb(self):
        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        entries = []
        for org, funcs in data.items():
            for func in funcs:
                entries.append({"org": org, "function": func})
        return entries

    def _load_or_compute_vecs(self):
        if self.vecs_path.exists():
            return np.load(self.vecs_path, allow_pickle=True)
        print(f"[KB] подсчет эмбеддингов...")
        texts = [e["function"] for e in self.kb_entries]
        vecs = np.array(self.encoder.encode(texts))
        np.save(self.vecs_path, vecs)
        return vecs

    def _load_or_compute_org_means(self):
        if self.org_means_path.exists():
            return np.load(self.org_means_path, allow_pickle=True).item()

        print("[KB] Подсчет средних эмбеддингов органов...")
        org_means = self._compute_org_embeddings()
        np.save(self.org_means_path, np.array(org_means, dtype=object), allow_pickle=True)
        return org_means

    def _load_or_build_faiss(self):
        d = self.kb_vecs.shape[1]
        if self.faiss_path.exists():
            print("[KB] загрузка faiss индексов")
            return faiss.read_index(str(self.faiss_path))
        print("[KB] построение faiss индексов")
        index = faiss.IndexFlatIP(d)
        index.add(self.kb_vecs.astype(np.float32))
        faiss.write_index(index, str(self.faiss_path))
        return index

    def _compute_org_embeddings(self):
        org_means = {}
        for org in set([e["org"] for e in self.kb_entries]):
            funcs = [e["function"] for e in self.kb_entries if e["org"] == org]
            vecs = np.array(self.encoder.encode(funcs))
            org_means[org] = vecs.mean(axis=0)
        return org_means

    def recompute(self):
        print(f"[KB] пересчет эмбеддингов...")
        texts = [e["function"] for e in self.kb_entries]
        vecs = np.array(self.encoder.encode(texts))
        np.save(self.vecs_path, vecs)
        self.kb_vecs = vecs

        org_means = self._compute_org_embeddings()
        np.save(self.org_means_path, np.array(org_means, dtype=object), allow_pickle=True)
        self.org_mean_vecs = org_means

        print("[KB] Перестроение FAISS индекса...")
        d = self.kb_vecs.shape[1]
        index = faiss.IndexFlatIP(d)
        index.add(self.kb_vecs.astype(np.float32))
        faiss.write_index(index, str(self.faiss_path))

    @property
    def size(self):
        return len(self.kb_entries)