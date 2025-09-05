import ast
import sys
from io import StringIO
from typing import Any, Dict
import pandas as pd
import numpy as np
import re
import datetime

from backend.models.schemas import ExecutionResultSchema


class ExecutionService:
    DANGEROUS_MODULES = {"os", "sys", "subprocess", "socket", "urllib", "requests"}
    
    DANGEROUS_FUNCTIONS = {"exec", "eval", "open"}
    
    SAFE_BUILTINS = {
        "len", "str", "int", "float", "bool", "list", "dict", "tuple", "set",
        "min", "max", "sum", "abs", "round", "sorted", "enumerate", "range",
        "zip", "map", "filter", "any", "all", "isinstance", "type", "print", "__import__", "import", "from", "pandas",
        "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
        "AttributeError", "ImportError", "RuntimeError", "StopIteration"
    }

    def __init__(self, max_script_length: int = 10000, timeout: int = 30):
        self.max_script_length = max_script_length
        self.timeout = timeout

    def validate_script(self, script: str) -> bool:
    
        if len(script) > self.max_script_length:
            return False

        try:
            tree = ast.parse(script)
        except SyntaxError:
            return False

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.DANGEROUS_MODULES:
                        return False
            
            elif isinstance(node, ast.ImportFrom):
                if node.module in self.DANGEROUS_MODULES:
                    return False
            
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_FUNCTIONS:
                        return False

        return True

    def create_safe_environment(self, df: pd.DataFrame) -> Dict[str, Any]:
        import builtins
        safe_builtins = {
            name: getattr(builtins, name) 
            for name in self.SAFE_BUILTINS 
            if hasattr(builtins, name)
        }

        return {
            "__builtins__": safe_builtins,
            "pd": pd,
            "np": np, 
            "re": re,
            "datetime": datetime,
            "df": df.copy() 
        }

    async def execute_script(self, script: str, original_df: pd.DataFrame) -> ExecutionResultSchema:
        try:
            if not self.validate_script(script):
                return ExecutionResultSchema(
                    error_message="Script did not pass validation"
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
                        error_message="Script have not return valid DataFrame"
                    )
                
                processed_df = safe_env["df"]
                
                return ExecutionResultSchema(
                    processed_dataframe=processed_df,
                    output=output or "Script executed without output",
                    processed_rows=len(processed_df)
                )
                
            except Exception as e:
                sys.stdout = old_output
                return ExecutionResultSchema(
                    error_message=f"Execution error: {str(e)}"
                )
                
        except Exception as e:
            return ExecutionResultSchema(
                error_message=f"General error: {str(e)}"
            )

    def clean_script(self, script: str) -> str:
        lines = script.split("\n")
        cleaned_lines = []

        for line in lines:
            stripped = line.strip()
            if not stripped or (stripped.startswith("#") and len(stripped) > 100):
                continue
                
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

execution_service = ExecutionService()