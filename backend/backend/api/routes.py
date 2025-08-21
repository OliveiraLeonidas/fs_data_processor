from datetime import datetime
from typing import Dict, Union

from backend.services.csv_service import CSVService
from fastapi import APIRouter, FastAPI, File, HTTPException, status, UploadFile

from backend.core.logging import setup_logging
from backend.models.schemas import ErrorResponseSchema, UploadResponseSchema

router = APIRouter()

log = setup_logging("routes.py")

FILE_UPLOAD_FOLDER: str = "upload"
PROCESSED_FOLDER: str = "processed"

csv_service = CSVService(str(FILE_UPLOAD_FOLDER), str(PROCESSED_FOLDER))


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponseSchema,
    responses={
        404: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema},
    },
)
async def upload(file: UploadFile = File(...)):
    log.info(f"POST /upload - upload file {file.filename} - size: {str(file.size)}")

    try:
        file_info = await csv_service.save_uploaded_file(file)

        log.info(f"File {file.filename} salved sucessfully: {file_info.file_id}")

        return UploadResponseSchema(
            filename=f"file: {file.filename} - id: {file_info.file_id}",
            status=True,
            message="FILE WAS UPLOADED SUCCESSFULLY",
        )

    except ValueError as e:
        log.error(e, "upload_csv - validation error")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        log.error(e, "upload_csv - unexpected error")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sorry, internal server error",
        )
