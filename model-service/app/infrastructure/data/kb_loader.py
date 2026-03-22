import json
from pathlib import Path


class KnowledgeBaseLoader:
    """Отвечает только за загрузку данных из JSON"""

    def __init__(self, kb_path: Path):
        self.kb_path = kb_path

    def load_entries(self) -> list[dict]:
        """
        Загружает записи из JSON.
        :return: Список всех органов и их полномочий.
        """
        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        entries = []
        for org, funcs in data.items():
            for func in funcs:
                entries.append({"org": org, "function": func})
        return entries

    def get_orgs(self, entries: list[dict]) -> list[str]:
        """
        Получает список уникальных органов.
        :param entries: Список всех органов и их полномочий.
        :return: Уникальные органы.
        """
        return list(set(e["org"] for e in entries))

    def get_funcs_by_org(self, entries: list[dict], org: str) -> list[str]:
        """Получает функции конкретного органа"""
        return [e["function"] for e in entries if e["org"] == org]
