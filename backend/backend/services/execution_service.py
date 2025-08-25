import ast
from io import StringIO
import sys
from typing import Any, Dict
from backend.models.schemas import ExecutionResultSchema
from backend.core.logging import setup_logging
from backend.core.settings import settings
import pandas as pd
import numpy as np
import re
import datetime

log = setup_logging("backend.route")


class ExecutionService:

    def __init__(self) -> None:
        self.timeout = settings.EXECUTION_TIMEOUT
        self.max_script_length = settings.MAX_SCRIPT_LENGTH

        self.block_list = {
            "__import__",
            "eval",
            "exec",
            "compile",
            "open",
            "file",
            "input",
            "raw_input",
            "reload",
            "vars",
            "dir",
            "globals",
            "locals",
            "delattr",
            "setattr",
            "getattr",
            "hasattr",
            "callable",
            "exit",
            "quit",
            "help",
            "license",
            "copyright",
            "credits",
            "abs",
            "all",
            "any",
            "bin",
            "bool",
            "bytearray",
            "bytes",
            "chr",
            "classmethod",
            "complex",
            "dict",
            "divmod",
            "enumerate",
            "filter",
            "float",
            "format",
            "frozenset",
            "hash",
            "hex",
            "id",
            "int",
            "isinstance",
            "issubclass",
            "iter",
            "len",
            "list",
            "map",
            "max",
            "memoryview",
            "min",
            "next",
            "object",
            "oct",
            "ord",
            "pow",
            "print",
            "property",
            "range",
            "repr",
            "reversed",
            "round",
            "set",
            "slice",
            "sorted",
            "staticmethod",
            "str",
            "sum",
            "super",
            "tuple",
            "type",
            "zip",
        }

    def validate_script(self, script: str) -> bool:
        try:
            if len(script) > self.max_script_length:
                log.warning("script is too long")
                return False

            tree = ast.parse(script)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in [
                            "os",
                            "sys",
                            "subprocess",
                            "socket",
                            "urllib",
                        ]:
                            log.warning(f"Dangerous import: {alias.name}")
                            return False

                if isinstance(node, ast.ImportFrom):
                    if node.module in ["os", "sys", "subprocess", "socket", "urllib"]:
                        log.warning(f"Dangerous import: : {node.module}")
                        return False

                # Verificar chamadas de função perigosas
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ["exec", "eval", "open", "__import__"]:
                            log.warning(f"Dangerous function: : {node.func.id}")
                            return False
            return True
        except SyntaxError as e:
            log.error(f"Erro de sintaxe no script: {e}")
            return False
        except Exception as e:
            log.error(f"Erro na validação do script: {e}")
            return False

    def create_safe_environment(self, df: pd.DataFrame) -> dict[str, Any]:
        safe_builtins = {
            "len",
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "tuple",
            "set",
            "min",
            "max",
            "sum",
            "abs",
            "round",
            "sorted",
            "enumerate",
            "range",
            "zip",
            "map",
            "filter",
            "any",
            "all",
            "isinstance",
        }

        # Ambiente restrito
        safe_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in safe_builtins
                if hasattr(__builtins__, name)
            },
            "pd": pd,
            "np": np,
            "re": re,
            "datetime": datetime,
            "df": df.copy(),  # Trabalhar com cópia para segurança
        }

        return safe_globals

    async def execute_script(
        self, script: str, original_df: pd.DataFrame
    ) -> ExecutionResultSchema:
        log.info("Execute scripting")

        try:
            if not self.validate_script(script):
                return ExecutionResultSchema(
                    success=False, error_message="Script did not pass validation"
                )

            safe_env = self.create_safe_environment(original_df)
            old_output = sys.stdout
            captured_output = StringIO()
            sys.stdout = captured_output

            try:
                exec(script, safe_env)

                sys.stdout = old_output
                output = captured_output.getvalue()

                if "df" not in safe_env:
                    return ExecutionResultSchema(
                        success=False,
                        error_message="Script have not return valid DataFrame",
                    )
                processed_df = safe_env["df"]

                if processed_df.empty:
                    return ExecutionResultSchema(
                        success=True,
                        output=output or "Script executed without output",
                        processed_rows=len(processed_df),
                        processed_dataframe=processed_df,
                    )
            except TimeoutError as er:
                sys.stdout = old_output
                log.error(f"Timeout execution: {er}")
                return ExecutionResultSchema(
                    success=False,
                    error_message=f"Execution exceed time limit { self.timeout}",
                )

            except Exception as e:
                sys.stdout = old_output
                log.error(f"Error execution script: {e}")
                return ExecutionResultSchema(
                    success=False, error_message=f"Execution error: {str(e)}"
                )
        except Exception as e:
            log.error(f"General execution error: {e}")
            return ExecutionResultSchema(
                success=False, error_message=f"General error: {str(e)}"
            )

    def clean_script(self, script: str) -> str:
        lines = script.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped or (stripped.startswith("#") and len(stripped) > 100):
                continue
            if stripped.startswith("import ") or stripped.startswith("from "):
                if any(
                    dangerous in stripped for dangerous in ["os", "sys", "subprocess"]
                ):
                    continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)


execution_service = ExecutionService()
