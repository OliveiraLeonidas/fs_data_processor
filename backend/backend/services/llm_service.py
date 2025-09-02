from dotenv import load_dotenv
from fastapi import HTTPException, status
from backend.core.logging import setup_logging
from google import genai
from google.genai import types
import os
from backend.core.logging import log_request

log = setup_logging("backend.llm_service")


class LLMService:
    client: str

    def __init__(self) -> None:
        log.info(f"Inicialize Gemini Service")
        load_dotenv()
        log.info(f"Gemini Service has been initialized")

    def initialize_gemini(self) -> None:
        genkey = os.getenv("GEMINI_SECRET_KEY")

        if not genkey:
            log.error("The GEMINI_SECRET_KEY was not found on .env")
            raise ValueError("Gemini API KEY not found")
        self.client = genai.Client(api_key=genkey)

        log.info("LLMService initialized succesfully.")

    def send_gen_request(self, system_instruction: str, content: str):
        log_request("Request Gemini API - Generate Content")
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                thinking_config=types.ThinkingConfig(
                    thinking_budget=0  
                ),
            ),
        )
        if not response:
            log.error("Missing response data")
            return HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "missing data content"},
            )
        return response.text

    def streaming_response(self, response: str):
        for chunk in response:
            print(chunk, end=" ")

    def get_system_prompt(self) -> str:
        system = """Você é um especialista em limpeza e tratamento de dados com Python e pandas.
                Sua tarefa é gerar um script Python que processe um DataFrame pandas chamado 'df' para limpar e tratar os dados.
                REGRAS IMPORTANTES:
                1. O script deve assumir que existe uma variável 'df' já carregada com os dados
                2. O script deve retornar o DataFrame limpo na variável 'df' (modificar in-place ou reatribuir)
                3. Sempre devolva o cabeçalho do dataframe em português do Brasil (first_name = "nome")
                4. Use apenas bibliotecas padrão: pandas, numpy, datetime, re
                5. Não use métodos ou funções que podem sofrer mudanças de versão do pandas
                6. Não importe bibliotecas - assuma que pandas está disponível como 'pd'
                7. Adicione comentários explicativos para cada operação
                8. Trate erros com try/except quando necessário
                9. Seja conservador - não remova dados desnecessariamente
                10. Foque em problemas comuns: valores nulos, duplicatas, tipos de dados incorretos, formatação
                11. Foque na eficiência - evite loops desnecessários

                Retorne APENAS o código Python, sem explicações adicionais antes ou depois."""
        return system


llm_service = LLMService()
