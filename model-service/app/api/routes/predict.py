from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from app.api.schemas.predict import PredictRequest
from app.core import container

router = APIRouter(prefix="/model", tags=["Model"])


@router.post("/predict")
async def predict(request: PredictRequest):
    """Эндпоинт для обработки текста"""
    result = await run_in_threadpool(container.pipeline.run, request.text)
    return result
