import re
import math
from typing import Any
import pymorphy3
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk

nltk.download('punkt_tab')


class Filtration:
    """Класс предобработки текста, фильтрует фразы оставляя максимум 70% исходного количества фраз в тексте"""

    def __init__(self):
        self.STOP_WORDS = {
            'высокий': ['уважаемый', 'здравствуйте', 'добрый день', 'доброе утро',
                        'добрый вечер', 'благодарю', 'спасибо', 'с уважением', 'прошу прощения',
                        'прошу разобраться', 'прошу сообщить', 'скажите когда', 'уведомите'],
            'низкий': ['прошу вас', 'будьте добры', 'очень прошу', 'крайне', 'чрезвычайно',
                       'обращение', 'жалоба', 'заявление',
                       'копия', 'вложение', 'приложение', 'документ'],
        }
        self.morph = pymorphy3.MorphAnalyzer()
        self.summarizer = LsaSummarizer()

    @staticmethod
    def _parse(text: str) -> tuple[list[str], Any]:
        """Разбиение текста на термы"""
        parser = PlaintextParser.from_string(text, Tokenizer("russian"))
        terms = [str(sentence) for sentence in parser.document.sentences]
        return terms, parser

    def _get_lsa_sum(self, terms: list[str], parser: Any) -> list[str]:
        """Получение топ термов из LSA"""
        num_sentences = math.ceil(len(terms) * 0.4)
        summary = self.summarizer(parser.document, num_sentences)
        summary_set = list(set(str(s) for s in summary))
        return summary_set

    @staticmethod
    def _score_lsa(term: str, summary_set: list[str]) -> int:
        """+3: содержится в топе lsa"""
        score = 0
        if term in summary_set:
            score = 3

        return score

    @staticmethod
    def _score_structure(term: str) -> int:
        """
        +1: начинается с глагола действия
        +1: содержит отрицание
        -2: слишком короткий
        -2: слишком длинный
        """
        score = 0
        words = term.lower().split()

        action_verbs = ['прошу', 'требую', 'сообщаю', 'жалуюсь', 'прошу', 'прошу']
        if any(term.lower().startswith(v) for v in action_verbs):
            score += 1

        if 'не' in words:
            score += 1

        if len(words) < 4:
            score -= 2

        if len(words) > 80:
            score -= 2

        return score

    @staticmethod
    def _score_thematic(term: str) -> int:
        """
        -2: содержит числа
        -2: адресный паттерн
        """
        score = 0
        term_lower = term.lower()

        if re.search(r'\d', term):
            score -= 2

        address_patterns = [r'ул\.\s*\w+', r'пр\.\s*\w+', r'д\.\s*\d+',
                            r'кв\.\s*\d+', r'г\.\s*\w+', r'\w+ская\s+обл']
        if any(re.search(p, term_lower) for p in address_patterns):
            score -= 2

        return score

    def _score_noise(self, term: str) -> int:
        """
        -2: формальное приветствие/заключение (стоп слова)
        -1: мета-упоминания (стоп слова)
        -2: капслок
        -1: >1 восклицательных знака
        """
        score = 0
        term_lower = term.lower()

        if any(sw in term_lower for sw in self.STOP_WORDS['высокий']):
            score -= 2

        if any(sw in term_lower for sw in self.STOP_WORDS['низкий']):
            score -= 1

        letters = [c for c in term if c.isalpha()]
        if letters and sum(1 for c in letters if c.isupper()) / len(letters) > 0.5:
            score -= 2

        if term.count('!') >= 2:
            score -= 1

        return score

    def _score_syntax(self, term: str) -> int:
        """
        -0.5: содержит именительный падеж
        -0.5: содержит винительный падеж
        +1: есть и глагол и существительное
        """
        score = 0
        words = term.split()[:15]

        cases = set()
        pos_tags = {'VERB': 0, 'NOUN': 0}

        for word in words:
            parsed = self.morph.parse(word.lower())
            if not parsed:
                continue

            p = parsed[0]
            if p.tag.case:
                cases.add(p.tag.case)
            if p.tag.POS in pos_tags:
                pos_tags[p.tag.POS] += 1

        if 'nomn' in cases:
            score -= 0.5

        if 'accs' in cases:
            score -= 0.5

        if pos_tags['VERB'] >= 1 and pos_tags['NOUN'] >= 1:
            score += 1

        return score

    @staticmethod
    def _check_duplicate(term: str, prev_terms: list[str]) -> int:
        """-3: совпадает на 60% с предыдущими термами"""
        if not prev_terms:
            return 0

        term_words = set(term.lower().split())
        if len(term_words) < 3:
            return 0

        for prev in prev_terms[-2:]:
            prev_words = set(prev.lower().split())
            intersection = term_words & prev_words
            union = term_words | prev_words

            if len(union) > 0 and len(intersection) / len(union) > 0.6:
                return -3

        return 0

    def filter(self, text: str) -> tuple[list[str], list[Any]]:
        """
        Фильтрует предложения по заданным правилам.
        :param text: Исходный текст.
        :return: Список отобранных фраз из текста и словарь с баллами для каждой фразы.
        """
        terms, parser = self._parse(text)

        lsa_summary = self._get_lsa_sum(terms, parser)

        scored_terms = []
        selected_terms = []

        for term in terms:
            details = {
                'structure': self._score_structure(term),
                'thematic': self._score_thematic(term),
                'noise': self._score_noise(term),
                'lsa': self._score_lsa(term, lsa_summary),
                'syntax': self._score_syntax(term),
                'duplicate': self._check_duplicate(term, selected_terms),
            }

            total_score = sum(details.values())

            scored_terms.append({
                'term': term,
                'score': total_score,
                'details': details,
            })

        scored_terms.sort(key=lambda x: -x['score'])

        positive = [st for st in scored_terms if st['score'] > 0]
        top_scored = positive[:math.ceil(len(terms) * 0.7)]
        top_terms = [r['term'] for r in top_scored]

        return top_terms, top_scored
