print("приложение поднимается пару минут...", flush=True)
import uvicorn
from fastapi import FastAPI

from app.api.routes import config, predict, recompute_kb, change_model
from app.core import container
from app.core.logger import get_logger

logger = get_logger("main")

app = FastAPI(title="Model Service")

app.include_router(predict.router)
app.include_router(config.router)
app.include_router(recompute_kb.router)
app.include_router(change_model.router)

try:
    logger.info("Инициализация пайплайна... это может занять пару секунд")
    container.pipeline = container.create_app_components()
    logger.info("Пайплайн готов! Сервис можно использовать")
except Exception as e:
    logger.exception(f"Ошибка при инициализации пайплайна: {e}")
    raise

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
