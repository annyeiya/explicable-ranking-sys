from fastapi import APIRouter
from pydantic import BaseModel
from app.api.routes.predict import pipeline  

router = APIRouter(prefix="/model", tags=["Config"])

class ConfigRequest(BaseModel):
    threshold: float | None = None
    num_sentences: int | None = None
    filter_type: str | None = None

@router.post("/config")
async def update_config(config: ConfigRequest):
    if config.threshold is not None:
        pipeline.matcher.threshold = config.threshold
    if config.num_sentences is not None:
        pipeline.num_sentences = config.num_sentences
        pipeline.filtration.num_sentences = config.num_sentences
    if config.filter_type is not None:
        pipeline.filter_type = config.filter_type
        pipeline.summarizer.method = config.filter_type
    return {"status": "ok", "current_config": {
        "threshold": pipeline.matcher.threshold,
        "num_sentences": pipeline.filtration.num_sentences,
        "summarizer_type": pipeline.filter_type
    }}

@router.get("/config")
async def get_config():
    return {"status": "ok", "current_config": {
        "threshold": pipeline.matcher.threshold,
        "num_sentences": pipeline.num_sentences,
        "summarizer_type": pipeline.filter_type
    }}