from typing import Any, Optional
from fastapi import UploadFile
from pydantic import BaseModel, Field


class BaseResponseSchema(BaseModel):
    message: str
    file_id: str


class UploadRequestSchema(BaseModel):
    file: UploadFile


class UploadResponseSchema(BaseModel):
    filename: str
    status: bool
    message: str


class FileInfoSchema(BaseModel):
    file_id: str
    filename: str
    file_path: str
    count_rows: int
    count_columns: int
    columns: list[str]


class ErrorResponseSchema(BaseModel):
    message: str


class DataSummarySchema(BaseModel):
    filename: str
    rows_count: int
    columns_count: int
    columns: list[str]
    data_types: dict[str, str]
    missing_values: dict[str, int]
    sample_rows: list[dict[str, Any]]
    duplicate_rows: int
    memory_usage: str


class ProcessResponseSchema(BaseResponseSchema):
    script: str
    data_summary: dict[str, Any]


class ExecutionResultSchema(BaseModel):
    success: bool
    output: Optional[str] = None
    error_message: Optional[str] = None
    processed_rows: Optional[int] = None


class ExecuteResponseSchema(BaseResponseSchema):
    execution_success: bool
    execution_output: Optional[str] = None
    error_message: Optional[str] = None
    processed_rows: Optional[int] = None


class ProcessedDataSchema(BaseModel):
    columns: list[str]
    data: list[dict[str, Any]]
    rows_count: int


class ResultResponseSchema(BaseResponseSchema):
    data: list[dict[str, Any]]
    columns: list[str]
    rows_count: int


class LLMRequestSchema(BaseModel):
    data_summary: DataSummarySchema

class LLMTestRequest(BaseModel):
    content: str

class LLMResponseSchema(BaseModel):
    script: str = Field(..., description="Script Python gerado")
    reasoning: Optional[str] = Field(None, description="Explicação do script")


class ValidationErrorSchema(BaseModel):
    field: str
    message: str
    value: Optional[Any] = None
