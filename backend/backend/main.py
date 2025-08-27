from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

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
