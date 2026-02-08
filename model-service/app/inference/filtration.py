from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
# from transformers import pipeline
import nltk
nltk.download('punkt_tab')

class Filtration:
    def __init__(self, num_sentences=4, method="lsa"):
        self.num_sentences = num_sentences
        self.method = method

        # self._neural_model = None
        # if self.method == "neural" and self._neural_model is None:
        #     self._init_neural_model()

    def _summarize_lsa(self, text):
        parser = PlaintextParser.from_string(text, Tokenizer("russian"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, self.num_sentences)
        return [str(sentence) for sentence in summary]

    # TODO модель надо найти нормальную, и учитывать количество предложений, мб юзать одну с комперссором
    # def _init_neural_model(self):
    #     if self._neural_model is None:
    #         self._neural_model = pipeline(
    #             "summarization",
    #             model="IlyaGusev/rut5_base_sum_gazeta",
    #             tokenizer="IlyaGusev/rut5_base_sum_gazeta"
    #         )

    # def _summarize_neural_model(self, text):
    #     self._init_neural_model()
    #     result = self._neural_model(
    #                         text,
    #                     )[0]['summary_text']
    #     return [s.strip() for s in result.split(". ") if s.strip()]

    def select_sentences(self, text):
        if self.method == "lsa":
            return self._summarize_lsa(text)
        # elif self.method == "neural":
        #     return self._summarize_neural_model(text)
        else:
            return text.split(". ")
