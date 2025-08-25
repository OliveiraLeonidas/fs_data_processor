import asyncio
from pathlib import Path
from typing import Optional
import aiofiles
import uuid
from backend.core.settings import settings
from backend.core.logging import setup_logging
from backend.models.schemas import (
    DataSummarySchema,
    FileInfoSchema,
    ProcessedDataSchema,
)
import pandas as pd

from fastapi import UploadFile
from fastapi.responses import JSONResponse

log = setup_logging("CSVService.py")


class CSVService:
    def __init__(self) -> None:
        log.info(f"Inicialize CSV Service")
        self.upload_dir = settings.UPLOAD_DIR
        self.processed_dir = settings.PROCESSED_DIR
        log.info(f"CSV Service has been initialized")

    async def save_uploaded_file(self, file: UploadFile) -> FileInfoSchema:
        try:
            file_id = str(uuid.uuid4())

            file_path = self.upload_dir / f"{file_id}.csv"

            async with aiofiles.open(file_path, "wb") as buffer:
                content = await file.read()
                await buffer.write(content)

            log.info(f"File salvo: {file_path}")

            df = await asyncio.get_event_loop().run_in_executor(
                None, pd.read_csv, str(file_path)
            )

            return FileInfoSchema(
                file_id=file_id,
                filename=file.filename or "unknown.csv",
                file_path=str(file_path),
                count_rows=len(df),
                count_columns=len(df.columns),
                columns=df.columns.tolist(),
            )

        except pd.errors.EmptyDataError:
            raise ValueError("File CSV está vazio")
        except pd.errors.ParserError as e:
            raise ValueError(f"Erro ao analisar CSV: {str(e)}")
        except Exception as e:
            log.error(e, "save_uploaded_file")
            raise

    def file_exists(self, file_id: str) -> bool:
        file_path = self.upload_dir / f"{file_id}.csv"
        return file_path.exists()

    def processed_file_exists(self, file_id: str) -> bool:
        file_path = self.processed_dir / f"{file_id}_processed.csv"
        return file_path.exists()

    async def get_data_summary(self, file_id: str) -> DataSummarySchema:
        try:
            file_path = self.upload_dir / f"{file_id}.csv"

            if not file_path.exists():
                raise FileNotFoundError(f"File {file_id} not found")

            df = await asyncio.get_event_loop().run_in_executor(
                None, pd.read_csv, str(file_path)
            )

            data_types = df.dtypes.astype(str).to_dict()
            missing_values = df.isnull().sum().to_dict()
            duplicate_rows = df.duplicated().sum()
            memory_usage = f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB"

            # limitado para economizar tokens
            sample_size = min(5, len(df))
            sample_rows = df.head(sample_size).fillna("").to_dict("records")

            return DataSummarySchema(
                filename=f"{file_id}.csv",
                rows_count=len(df),
                columns_count=len(df.columns),
                columns=df.columns.tolist(),
                data_types=data_types,
                missing_values=missing_values,
                sample_rows=sample_rows,
                duplicate_rows=int(duplicate_rows),
                memory_usage=memory_usage,
            )

        except Exception as e:
            log.error(e, f"get_data_summary - file_id: {file_id}")
            raise

    async def save_script(self, file_id: str, script: str) -> None:
        try:
            script_path = self.upload_dir / f"{file_id}_script.py"

            script = self.format_script(script=script)

            async with aiofiles.open(script_path, "w", encoding="utf-8") as f:
                await f.write(script)

            log.info(f"Script was salved in: {script_path}")

        except Exception as e:
            log.error(e, f"save_script - file_id: {file_id}")
            raise

    async def get_script(self, file_id: str) -> Optional[str]:
        try:
            script_path = self.upload_dir / f"{file_id}_script.py"

            if not script_path.exists():
                return None

            async with aiofiles.open(script_path, "r", encoding="utf-8") as f:
                script = await f.read()

            return script

        except Exception as e:
            log.error(e, f"get_script - file_id: {file_id}")
            raise

    async def save_processed_data(self, file_id: str, df: pd.DataFrame) -> None:
        try:
            processed_path = self.processed_dir / f"{file_id}_processed.csv"

            await asyncio.get_event_loop().run_in_executor(
                None, df.to_csv, str(processed_path), False  # index=False
            )

            log.info(f"Dados processados salvos: {processed_path}")

        except Exception as e:
            log.error(e, f"save_processed_data - file_id: {file_id}")
            raise

    async def get_processed_data(self, file_id: str) -> ProcessedDataSchema:
        try:
            processed_path = self.processed_dir / f"{file_id}_processed.csv"

            if not processed_path.exists():
                raise FileNotFoundError(f"File processed {file_id} was not found")

            df = await asyncio.get_event_loop().run_in_executor(
                None, pd.read_csv, str(processed_path)
            )

            data = df.fillna("").to_dict("records")

            return ProcessedDataSchema(
                columns=df.columns.tolist(),
                data=data,
                rows_count=len(df),
            )

        except Exception as e:
            log.error(e, f"get_processed_data - file_id: {file_id}")
            raise

    async def get_original_dataframe(self, file_id: str) -> pd.DataFrame:
        try:
            file_path = self.upload_dir / f"{file_id}.csv"

            if not file_path.exists():
                raise FileNotFoundError(f"File {file_id} not found")

            df = await asyncio.get_event_loop().run_in_executor(
                None, pd.read_csv, str(file_path)
            )

            return df

        except Exception as e:
            log.error(e, f"get_original_dataframe - file_id: {file_id}")
            raise

    async def cleanup_files(self, file_id: str) -> None:
        try:
            files_to_remove = [
                self.upload_dir / f"{file_id}.csv",
                self.upload_dir / f"{file_id}_script.py",
                self.processed_dir / f"{file_id}_processed.csv",
            ]

            for file_path in files_to_remove:
                if file_path.exists():
                    file_path.unlink()
                    log.info(f"File removed: {file_path}")

        except Exception as e:
            log.error(e, f"cleanup_files - file_id: {file_id}")

    def format_script(self, script: str):
        if script.startswith("```python"):
            script = script[9:]
        if script.endswith("```"):
            script = script[:-3]
        script = script.strip()
        return script


csv_service = CSVService()
