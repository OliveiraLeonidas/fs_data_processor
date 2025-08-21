import os
from dotenv import load_dotenv

load_dotenv()
geminiapi = os.getenv("GEMINI_SECRET_KEY")

print(f"Conectando: {geminiapi}")
