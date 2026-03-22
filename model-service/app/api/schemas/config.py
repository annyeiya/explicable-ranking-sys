from pydantic import BaseModel


class ConfigRequest(BaseModel):
    threshold: float | None = None
    top_k_func: int | None = None
    top_k_org: int | None = None
