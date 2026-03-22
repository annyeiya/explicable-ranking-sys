from fastapi import APIRouter

from app.core import container

router = APIRouter(prefix="/model", tags=["Model"])


@router.post("/recompute_kb")
def recompute_kb():
    """Эндпоинт для перестроения векторной базы знаний"""
    container.pipeline.kb_recompute()
    return {"status": "ok", "message": "База знаний пересчитана"}
