import traceback
from typing import Optional

from backend.services import execution_service
from backend.services.execution_service import ExecutionService
from backend.core.settings import settings
from backend.services.csv_service import CSVService, csv_service
from backend.services.llm_service import LLMService, llm_service
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

    try:
        if not file.filename or not file.filename.endswith(".csv"):
            raise ValueError("File must be an valid csv file")

        if not file.size or file.size > settings.MAX_FILE_SIZE:
            raise ValueError("File is to large (max: 10MB)")

        file_info = await csv_service.save_uploaded_file(file)
        log.info(f"File {file.filename} salved successfully: {file_info.file_id}")

        return UploadResponseSchema(
            filename=f"file: {file.filename} - id: {file_info.file_id}",
            status=True,
            message="FILE WAS UPLOADED SUCCESSFULLY",
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
        print(data_summary)
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
                    4. Padronize formatação (datas, emails, etc.)
                    5. Remova linhas/colunas inválidas se necessário

                    O script deve modificar o DataFrame 'df' in-place ou reatribuí-lo.
                    """

        llm_service.initialize_gemini()
        system = llm_service.get_system_prompt()
        script = llm_service.send_gen_request(system_instruction=system, content=prompt)
        await csv_service.save_script(file_id=file_id, script=script)
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
    """Executa o script gerado pela LLM nos dados"""
    log_request(f"POST /execute: {file_id}")

    try:
        # Verificar se arquivo e script existem
        if not csv_service.file_exists(file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
            )

        script = await csv_service.get_script(file_id)
        if not script:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Script não encontrado. Execute /process primeiro.",
            )

        # Carregar dados originais
        original_df = await csv_service.get_original_dataframe(file_id)

        # Executar script
        result = await execution_service.execute_script(script, original_df)

        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro na execução do script: {result.error_message}",
            )

        # Salvar dados processados
        await csv_service.save_processed_data(file_id, result.processed_dataframe)

        log.info(f"Script executado com sucesso para file_id: {file_id}")

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
            detail="Erro ao executar script",
        )


@router.get(
    "/result/{file_id}",
    response_model=ResultResponseSchema,
    responses={
        404: {"model": ErrorResponseSchema},
    },
)
async def get_result(file_id: str, csv_service: CSVService = Depends(get_csv_service)):
    """Obtém o resultado final do processamento"""
    log_request(f"GET /result - file: {file_id}")

    try:
        if not csv_service.processed_file_exists(file_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Arquivo processado não encontrado. Execute /execute primeiro.",
            )

        processed_data = await csv_service.get_processed_data(file_id)

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
            detail="Erro ao obter resultado",
        )


@router.get("/status/{file_id}", responses={404: {"model": ErrorResponseSchema}})
async def get_status(file_id: str, csv_service: CSVService = Depends(get_csv_service)):
    """Verifica o status do processamento de um arquivo"""
    log_request(f"GET /status - file: {file_id}")

    try:
        has_original = csv_service.file_exists(file_id)
        has_script = await csv_service.get_script(file_id) is not None
        has_processed = csv_service.processed_file_exists(file_id)

        if not has_original:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado"
            )

        status_info = {
            "file_id": file_id,
            "uploaded": has_original,
            "processed_by_llm": has_script,
            "script_executed": has_processed,
            "ready": has_processed,
        }

        return status_info

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Error getting status for file {file_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao obter status",
        )
