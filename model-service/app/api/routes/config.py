from fastapi import APIRouter

from app.api.schemas.config import ConfigRequest
from app.core.state import State

router = APIRouter(prefix="/model", tags=["Config"])


@router.post("/config")
def update_config(config: ConfigRequest):
    """Эндпоинт для изменения гиперпараметров системы"""
    if config.threshold is not None:
        State.threshold = config.threshold
    if config.top_k_func is not None:
        State.top_k_func = config.top_k_func
    if config.top_k_org is not None:
        State.top_k_org = config.top_k_org
    return {"status": "ok", "current_config": {
        "threshold": State.threshold,
        "top_k_func": State.top_k_func,
        "top_k_org": State.top_k_org
    }}


@router.get("/config")
async def get_config():
    """Эндпоинт для получения гиперпараметров системы"""
    return {"status": "ok", "current_config": {
        "threshold": State.threshold,
        "top_k_func": State.top_k_func,
        "top_k_org": State.top_k_org,
        "torch_model": State.torch_model
    }}
