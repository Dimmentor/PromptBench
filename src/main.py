from contextlib import asynccontextmanager
from multiprocessing import cpu_count

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.core.logger import logger
from src.interfaces.api.endpoints.tests import router as tests_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Запуск PromptBench Backend")
        yield
    except Exception as e:
        logger.error(f"Ошибка при запуске приложения: {e}")
        raise
    finally:
        logger.info("PromptBench Backend останавливается...")

app = FastAPI(lifespan=lifespan, title="PromptBench", description="Примерное API для прогона промптов и параметров")

app.include_router(tests_router)

@app.get("/healthcheck")
async def health():
    return {"message": "PromptBench API is running"}


workers_count = 1 # workers_count = (cpu_count() * 2) + 1

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8020,
        workers=workers_count,
        log_level="info",
        timeout_keep_alive=30,
        limit_concurrency=10,  # Ограничение одновременных запросов
        limit_max_requests=1000,  # Перезапуск worker после 1K запросов (защита от утечек памяти)
    )