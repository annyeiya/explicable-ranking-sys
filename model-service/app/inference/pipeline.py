from app.inference.compressor import Compressor
from app.inference.encoder import Encoder
from app.inference.filtration import Filtration
from app.inference.global_scorer import GlobalScorer
from app.inference.matcher import Matcher
from app.inference.kb import KnowledgeBase

class Pipeline:
    def __init__(self, num_sentences=4, threshold=0.4, filter_type="lsa"):
        self.encoder = Encoder()
        self.num_sentences = num_sentences
        self.threshold = threshold
        self.filter_type = filter_type
        self.filtration = Filtration(
                        num_sentences=self.num_sentences,
                        method=self.filter_type
                    )
        self.kb = KnowledgeBase(encoder=self.encoder)
        self.matcher = Matcher(
                        self.kb,
                        threshold=self.threshold,
                        encoder=self.encoder
                    )
        self.compressor = Compressor()
        self.global_scorer = GlobalScorer(self.encoder, self.kb, self.compressor)

    def run(self, text):
        phrases = self.filtration.select_sentences(text)
        print(f"отобранные фразы: {phrases}")
        compressed_phrases, mapping = self.compressor.compress_sentence(phrases)
        print(f"обработанные фразы: {compressed_phrases}")
        matches = self.matcher.math(compressed_phrases)
        global_bonus = self.global_scorer.get_context_scores(text)
        for m in matches:
            m["text_phrase"] = mapping.get(m["text_phrase"], m["text_phrase"])
            org = m["org"]
            m["context_boost"] = round(float(global_bonus.get(org, 0.0)), 3)

        return matches

    def recompute_kb(self):
        self.kb.recompute()