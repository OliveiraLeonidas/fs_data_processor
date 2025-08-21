

from fastapi import UploadFile
from pydantic import BaseModel


class UploadRequestSchema(BaseModel):
    file: UploadFile

class UploadResponseSchema(BaseModel):
    filename: str
    status: bool
    message: str

class FileInfo(BaseModel):
    file_id: str
    filename: str
    filetype: str
    count_rows: str
    count_columns: str

class ErrorResponseSchema(BaseModel):
    message: str