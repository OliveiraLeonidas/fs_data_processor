from datetime import datetime
from pathlib import Path
from typing import Dict, Union

from backend.services.csv_service import CSVService
from fastapi import APIRouter, FastAPI, File, HTTPException, status, UploadFile
from backend.api.routes import router

from backend.core.logging import setup_logging
from backend.models.schemas import ErrorResponseSchema, UploadResponseSchema

app = FastAPI(title="Data Processor - Cleaning CSV Data with LLM")


log = setup_logging("main.py")

app.include_router(router=router, prefix="/api/v1")


@app.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "message": "CSV Processor API is running"}
