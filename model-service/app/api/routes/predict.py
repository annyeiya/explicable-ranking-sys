from fastapi import APIRouter
from pydantic import BaseModel
from app.inference.pipeline import Pipeline

router = APIRouter(prefix="/model", tags=["Model"])
print("[INFO] Инициализация пайплайна... это может занять пару секунд")
pipeline = Pipeline()
print("[INFO] Пайплайн готов! Сервис можно использовать")

class PredictRequest(BaseModel):
    text: str

@router.post("/predict")
async def predict(request: PredictRequest):
    result = pipeline.run(request.text)
    return {"result": result}

@router.post("/recompute_kb")
async def recompute_kb():
    pipeline.recompute_kb()
    return {"status": "ok", "message": "База знаний пересчитана"}