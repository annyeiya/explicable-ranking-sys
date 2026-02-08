import uvicorn
from fastapi import FastAPI
from app.api.routes import predict, config

app = FastAPI(title="Model Service")
app.include_router(predict.router)
app.include_router(config.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)