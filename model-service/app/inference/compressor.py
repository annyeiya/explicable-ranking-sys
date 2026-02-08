import nltk
nltk.download('punkt')
# from transformers import pipeline

# сам компрессор по сути не работает, надо модельку подобрать :)
class Compressor:
    def __init__(self, len_sentence_threshold=100):
        self.len_sentence_threshold = len_sentence_threshold
        print("[INFO] Инициализация нейронной модели саммаризации...")
        # TODO модель :(
        # self.model = pipeline("summarization", model="IlyaGusev/rut5_base_sum_gazeta")

    def compress_sentence(self, sentences):
        mapping = {}
        compressed = []
        for s in sentences:
            # word_count = len(s.split())
            # if word_count > self.len_sentence_threshold:
            #     summary = self.model(
            #         s,
            #         max_length=min(20, word_count // 2),
            #         min_length=5,
            #         do_sample=False
            #     )[0]["summary_text"]
            #     compressed.append(summary)
            #     mapping[summary] = s
            # else:
                # compressed.append(s)
                # mapping[s] = s
            compressed.append(s)
            mapping[s] = s

        return compressed, mapping

    def summarize_text(self, text):
        # summary = self.model(
        #     text,
        #     max_length=64,
        #     min_length=20,
        #     do_sample=False
        # )[0]["summary_text"]
        # return summary
        return text