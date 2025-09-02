from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

from backend.core.cache_db import cache_db
from backend.services.csv_service import csv_service
from backend.core.logging import setup_logging
from backend.core.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API to process csv files using LLM",
    version="1.0.0",
)

log = setup_logging("backend.main")

app.include_router(router=router, prefix="/api/v1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "message": "CSV Processor API is running"}

@app.get('/data')
async def data(file_id: str):
    print(file_id)
    data_summary = await csv_service.get_data_summary(file_id)
    return data_summary

@app.get('/redis/{file_id}')
async def redis_status(file_id: str):
    status = cache_db.get_status(file_id)
    return status