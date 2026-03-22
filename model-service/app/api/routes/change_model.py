from fastapi import APIRouter

from app.core import container
from app.core.state import State

router = APIRouter(prefix="/model", tags=["Config"])


@router.post("/change_model")
def update_config():
    """Эндпоинт для изменения модели: torch модель либо sentence-transformers"""
    State.torch_model = not State.torch_model
    container.pipeline = container.create_app_components()
    container.pipeline.kb_recompute()
    return {
        "status": "ok", "model_state": "torch" if State.torch_model else "sent-trans"
    }
