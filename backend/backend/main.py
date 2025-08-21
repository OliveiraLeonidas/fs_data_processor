from datetime import datetime
import logging
from typing import Dict, Union

from fastapi import FastAPI, File, HTTPException, status, UploadFile

from backend.core.logging import setup_logging
from backend.models.schemas import ErrorResponseSchema, UploadResponseSchema

app = FastAPI(
    title="Data Processor - Cleaning CSV Data with LLM"
)


log = setup_logging('main.py')

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.post("/upload", status_code=status.HTTP_201_CREATED, response_model=UploadResponseSchema, responses={
        404: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema}
    })
async def upload(file: UploadFile = File(...)):
    log.info(f"Request into /upload - upload file {file.filename} - size: {str(file.size)}")
    content = await file.read()

    if file.filename.endswith('.txt'):
        log.info(f"")
        return UploadResponseSchema(
            filename=file.filename,
            status=True,
            message="UPLOAD_SUCCESSED"
        )
    raise HTTPException(
            status_code=400,
            detail=f"Something goes wrong with filename: {file.filename} at: {datetime.now()}"
        )