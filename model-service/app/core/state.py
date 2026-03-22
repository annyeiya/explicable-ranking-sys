"""Гиперпараметры системы"""


class State:
    threshold: float = 0.5
    top_k_func: int = 2
    top_k_org: int = 5
    torch_model: bool = True
