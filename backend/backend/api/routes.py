from io import BytesIO
import traceback

from fastapi.responses import FileResponse, StreamingResponse

from backend.core.settings import settings
from backend.services.execution_service import ExecutionService, execution_service
from backend.services.csv_service import CSVService, csv_service
from backend.services.llm_service import LLMService, llm_service
from backend.core.cache_db import cache_db
from fastapi import APIRouter, Depends, File, HTTPException, Query, status, UploadFile

from backend.core.logging import log_error, log_request, setup_logging
from backend.models.schemas import (
    ErrorResponseSchema,
    ExecuteResponseSchema,
    ProcessResponseSchema,
    ResultResponseSchema,
    UploadResponseSchema,
)

router = APIRouter()
log = setup_logging("backend.route")


def get_csv_service() -> CSVService:
    return csv_service


def get_llm_service() -> LLMService:
    return llm_service


def get_execution_service() -> ExecutionService:
    return execution_service


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    response_model=UploadResponseSchema,
    responses={
        404: {"model": ErrorResponseSchema},
        422: {"model": ErrorResponseSchema},
    },
)
async def upload(
    file: UploadFile = File(...), csv_service: CSVService = Depends(get_csv_service)
):
    log_request(f"POST /upload - filename: {file.filename}, size: {file.size}")

    log.info('Starting status object info into redis cache db')
    

    try:
        if not file.filename or not file.filename.endswith(".csv"):
            raise ValueError("File must be an valid csv file")

        if not file.size or file.size > settings.MAX_FILE_SIZE:
            raise ValueError("File is to large (max: 10MB)")

        file_info = await csv_service.save_uploaded_file(file)
        log.info(f"File {file.filename} salved successfully: {file_info.file_id}")

        cache_db.initialize_hash(file_info.file_id)
        cache_db.update_status(file_info.file_id, "uploaded", True)
        log.info("File status updated into redis cache db")

        return UploadResponseSchema(
            filename=f"file: {file.filename} - id: {file_info.file_id}",
            file_id=file_info.file_id,
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
async def process(
    file_id: str = Query(..., description="send file id"),
    csv_service: CSVService = Depends(get_csv_service),
    llm_service: LLMService = Depends(get_llm_service),
):
    
    log_request(f"POST /process - file: {file_id}")
    try:
        if not csv_service.file_exists(file_id=file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )
        data_summary = await csv_service.get_data_summary(file_id)

        prompt = f"""
                    Analise os dados CSV abaixo e gere um script Python para limpeza:

                    **Informações do Dataset:**
                    - Arquivo: {data_summary.filename}
                    - Linhas: {data_summary.rows_count}
                    - Colunas: {data_summary.columns_count}
                    - Colunas: {', '.join(data_summary.columns)}

                    **Tipos de Dados:**
                    {chr(10).join([f"- {col}: {dtype}" for col, dtype in data_summary.data_types.items()])}

                    **Valores Faltantes:**
                    {chr(10).join([f"- {col}: {count}" for col, count in data_summary.missing_values.items() if count > 0])}

                    **Linhas Duplicadas:** {data_summary.duplicate_rows}

                    **Amostra dos Dados:**
                    {chr(10).join([str(row) for row in data_summary.sample_rows[:3]])}

                    Gere um script Python que:
                    1. Trate valores nulos de forma inteligente
                    2. Remova duplicatas se necessário
                    3. Corrija tipos de dados
                    4. Padronize formatação (datas, emails, nomes, etc.)
                    5. Remova linhas/colunas inválidas se necessário
                    6. caso existe colunas com sequências numéricas, verifique se existem gaps e tente preenchê-los
                    7. se uma sequencia de datas estiver incompleta, tente preenchê-la
                    

                    O script deve modificar o DataFrame 'df' in-place ou reatribuí-lo.
                    """

        # llm_service.initialize_gemini()
        # system = llm_service.get_system_prompt()
        # script = llm_service.send_gen_request(system_instruction=system, content=prompt)

        llm_service.initialize_openai()
        system = llm_service.get_system_prompt()
        script = llm_service.send_openai_request(system_instruction=system, content=prompt)
        await csv_service.save_script(file_id=file_id, script=script)
        
        log.info(f'Redis cachedb updated - Processed by LLM: {file_id}')
        cache_db.update_status(file_id, "processed_by_llm", True)
        return ProcessResponseSchema(
            file_id=file_id,
            message="Data Transformation was succesfully generated",
            script=script,
            data_summary=data_summary.model_dump(),
        )

    except HTTPException as http:
        log_error(f"Error HTTP: {http}")
        raise
    except Exception as exc:
        log.error(f"Error processing file {file_id}: {exc}")
        log.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing file with LLM",
        )


@router.post(
    "/execute",
    response_model=ExecuteResponseSchema,
    responses={
        400: {"model": ErrorResponseSchema},
        404: {"model": ErrorResponseSchema},
    },
)
async def execute_script(
    file_id: str = Query(..., description="file id"),
    csv_service: CSVService = Depends(get_csv_service),
    execution_service: ExecutionService = Depends(get_execution_service),
):
    log_request(f"POST /execute: {file_id}")

    try:
        if not csv_service.file_exists(file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        script = await csv_service.get_script(file_id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found. Execute /process first.",
            )

        original_df = await csv_service.get_original_dataframe(file_id)
        print(original_df.head())
        result = await execution_service.execute_script(script, original_df)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error when trying to execute script: {result.error_message}",
            )

        await csv_service.save_processed_data(file_id, result.processed_dataframe)
        log.info(f"Script successfully executed into file_id: {file_id}")

        log.info(f'Redis cachedb updated - Script executed: {file_id}')
        cache_db.update_status(file_id, "script_executed", True)

        return ExecuteResponseSchema(
            file_id=file_id,
            message="Script executado com sucesso",
            execution_success=True,
            execution_output=result.output,
            processed_rows=result.processed_rows,
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error executing script for file {file_id}: {e}")
        log.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error when trying to execute script",
        )


@router.get(
    "/download/{file_id}",
    responses={
        404: {"model": ErrorResponseSchema},
    },
)
async def download(file_id: str, csv_service: CSVService = Depends(get_csv_service)):
    log_request(f"GET /result - file: {file_id}")

    try:
        if not csv_service.processed_file_exists(file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo processado não encontrado. Execute /execute primeiro.",
            )

        processed_path = csv_service.processed_dir / f"{file_id}_processed.csv"
        print("File status updated into redis cache db - ready: True")
        print('file path: ' + str(processed_path))
        

        cache_db.update_status(file_id, "ready", True)
        print(f'File status updated into redis cachedb - {cache_db.get_status(file_id)}')
        # cache_db.delete_status()
        return FileResponse(
            path=str(processed_path),
            media_type='text/csv',
            filename=f"{file_id}_report_processed.csv",
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting result for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eror to get result",
        )

@router.get(
    "/result/{file_id}",
    responses={
        404: {"model": ErrorResponseSchema},
    },
)
async def get_result(file_id: str, csv_service: CSVService = Depends(get_csv_service)):
    log_request(f"GET /result - file: {file_id}")

    try:
        if not csv_service.processed_file_exists(file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo processado não encontrado. Execute /execute primeiro.",
            )

        processed_path = csv_service.processed_dir / f"{file_id}_processed.csv"
        processed_data = await csv_service.get_processed_data(file_id)
        print("File status updated into redis cache db - ready: True")
        print('file path: ' + str(processed_path))
        

        cache_db.update_status(file_id, "ready", True)
        return ResultResponseSchema(
            file_id=file_id,
            message="Dados processados obtidos com sucesso",
            data=processed_data.data,
            columns=processed_data.columns,
            rows_count=processed_data.rows_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting result for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Eror to get result",
        )


@router.get('/clean/{file_id}')
async def clean(file_id: str):
    print(f'File status updated into redis cachedb - {cache_db.get_status(file_id)}')
    cache_db.delete_status(file_id)

@router.get("/status/{file_id}", responses={404: {"model": ErrorResponseSchema}})
async def get_status(file_id: str, csv_service: CSVService = Depends(get_csv_service)):
    log_request(f"GET /status - file: {file_id}")

    try:
        has_original = csv_service.file_exists(file_id)
        status_info = cache_db.get_status(file_id)

        if not has_original or not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting status for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving status",
        )


@router.get("/script/{file_id}", responses={404: {"model": ErrorResponseSchema}})
async def get_script(file_id: str, csv_service: CSVService = Depends(get_csv_service)):
    try:
        script = await csv_service.get_script(file_id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script not found for this file_id",
            )
        file_stream = BytesIO(script.encode('utf-8'))
        return StreamingResponse(
            file_stream,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={file_id}_script.py"},
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting script for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving script",
        )