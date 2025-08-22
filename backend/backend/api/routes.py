from datetime import datetime
import logging
from typing import Dict, Union

from fastapi.responses import JSONResponse, PlainTextResponse

from backend.services.csv_service import CSVService, csv_service
from backend.services.llm_service import LLMService, llm_service
from fastapi import APIRouter, Depends, FastAPI, File, HTTPException, status, UploadFile

from backend.core.logging import log_request, setup_logging
from backend.models.schemas import ErrorResponseSchema, LLMTestRequest, UploadResponseSchema

router = APIRouter()
log = setup_logging("backend.route")

def get_csv_service() -> CSVService:
    return csv_service

def get_llm_service() -> LLMService:
    return llm_service


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponseSchema,
    responses={
        404: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema},
    },
)
async def upload(file: UploadFile = File(...), csv_service: CSVService = Depends(get_csv_service)):
    log_request("POST /upload", filename=file.filename, size=file.size)

    try:
        file_info = await csv_service.save_uploaded_file(file)
        log.info(f"File {file.filename} salved successfully: {file_info.file_id}")




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


@router.post("/process")
def process(
    content: LLMTestRequest, 
    file_id: str, 
    csv_service: CSVService = Depends(get_csv_service), 
    llm_service: LLMService = Depends(get_llm_service)):
    print(content)
    log.info(f"POST /process - processing file {file_id} - size:")



    llm_service.initialize_gemini()
    system = llm_service.get_system_prompt()
    script_gerado = llm_service.send_gen_request(system, content.content)
    
    
    print("--- RESPOSTA DA API ---")
    print(PlainTextResponse(script_gerado, media_type="text/plain"))
    print("-----------------------")
    
    return PlainTextResponse(script_gerado, media_type="text/plain")