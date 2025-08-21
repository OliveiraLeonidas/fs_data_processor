# AI CSV Cleaner - Avaliação Técnica Fullstack

Este projeto é uma aplicação web fullstack desenvolvida como parte de uma avaliação técnica. A aplicação permite que usuários façam o upload de um arquivo CSV, que é então analisado por um Large Language Model (LLM) para gerar dinamicamente um script de limpeza em Python. O script é executado no backend para tratar os dados, e o resultado final é exibido ao usuário.

## ✨ Features Principais

- **Upload de Arquivo CSV**: Interface intuitiva para o upload de arquivos.
- **Geração de Script com IA**: Utiliza a API do Google Gemini (ou outra LLM) para analisar os dados e gerar um script de limpeza com a biblioteca `pandas`.
- **Execução Segura**: O script gerado é executado em um ambiente controlado no backend.
- **Visualização de Resultados**: Exibe o CSV tratado em uma tabela na interface.
- **Feedback de Progresso**: O usuário é informado sobre cada etapa do processo (upload, processamento, finalização).

## 🚀 Tech Stack

| Área                   | Tecnologia / Biblioteca                                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Frontend**           | [Next.js](https://nextjs.org/), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/)         |
| **UI & Estilização**   | [Shadcn/UI](https://ui.shadcn.com/), [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4-alpha)          |
| **Backend**            | [Python](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/)                                        |
| **Gerenciamento (BE)** | [Poetry](https://python-poetry.org/) para dependências, [Taskipy](https://github.com/taskipy/taskipy) para scripts |
| **Integração IA**      | [Google Generative AI](https://ai.google.dev/) (ou OpenAI)                                                         |

## 📋 Características

- **FastAPI** - Framework moderno e performático para APIs
- **Poetry** - Gerenciamento de dependências e ambientes virtuais
- **Ruff** - Linting e formatação de código ultrarrápida
- **OpenAI Integration** - Integração com GPT para geração de scripts de limpeza
- **Logging Estruturado** - Sistema de logs robusto

## 🏗️ Arquitetura

```
app/
├── api/
│   └── routes.py
├── core/
│   └── logging.py
├── models/
│   └── schemas.py
├── services/
│   ├── csv_service.py
└── main.py
```

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.13+
- Poetry
- Chave da API OpenAI | Google Gemini

### Instalação

1. **Clone o repositório**

```bash
    git clone https://github.com/OliveiraLeonidas/fs_data_processor.git
    cd csv-processor-api
```

2. **Configure as variáveis de ambiente**

```bash
    cp .env.example .env
# Edite .env e adicione sua GEMINI_SECRET_KEY
```

3. **Execute a aplicação**

```bash
    poetry run task run
```

A API estará disponível em `http://localhost:8000/docs`

## 📚 Endpoints da API

### Upload de CSV

```http
    POST /api/v1/upload
    Content-Type: multipart/form-data

file: arquivo.csv
```

### Processar com LLM

```http
    POST /api/v1/process?file_id={file_id}
```

### Executar Script

```http
    POST /api/v1/execute?file_id={file_id}
```

### Obter Resultado

```http
    GET /api/v1/result/{file_id}
```

## 🔧 Desenvolvimento

### Comandos Disponíveis

inicialmente rode `poetry shell`

```bash
    poetry install
    poetry run task run
    poetry run task test
    poetry run task lint
    poetry run task format
```

### Estrutura de Qualidade de Código

O projeto utiliza as seguintes ferramentas para garantir qualidade:

- **Ruff** - Linting e formatação rápida
- **Taskipy** - Atalhos para comandos
- **Pytest** - Framework de testes

## 🔒 Segurança

A aplicação implementa várias camadas de segurança:

### Validação de Arquivos

- Verificação de extensão (apenas .csv)
- Limite de tamanho de arquivo (10MB)
- Validação de nome de arquivo

### Execução Segura de Scripts

- Ambiente de execução restrito
- Timeout para execução (30s)
- Blacklist de funções perigosas
- Validação de sintaxe antes da execução

### Variáveis de Ambiente

- Chaves de API armazenadas em variáveis de ambiente
- Configurações sensíveis isoladas

## 📊 Fluxo de Processamento

1. **Upload** - Cliente envia arquivo CSV
2. **Análise** - Sistema extrai metadados e amostra dos dados
3. **LLM Processing** - LLM gera script de limpeza personalizado
4. **Execução** - Script é executado em ambiente seguro
5. **Resultado** - Dados limpos são retornados ao cliente

## 🧪 Exemplo de Uso

1. **Faça upload de um CSV**

```bash
    curl -X POST "http://localhost:8000/api/v1/upload" \
        -H "Content-Type: multipart/form-data" \
        -F "file=@exemplo.csv"
```

2. **Processe com LLM**

```bash
    curl -X POST "http://localhost:8000/api/v1/process?file_id=123e4567-e89b-12d3-a456-426614174000"
```

3. **Execute o script**

```bash
   curl -X POST "http://localhost:8000/api/v1/execute?file_id=123e4567-e89b-12d3-a456-426614174000"
```

4. **Obtenha o resultado**

```bash
   curl -X GET "http://localhost:8000/api/v1/result/123e4567-e89b-12d3-a456-426614174000"
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Execute os testes e verificações de qualidade (`make quality`)
4. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
5. Push para a branch (`git push origin feature/AmazingFeature`)
6. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🆘 Suporte

Para dúvidas ou problemas:

1. Verifique a documentação da API em `http://localhost:8000/docs`
2. Consulte os logs da aplicação
3. Abra uma issue no repositório

---

**Author: Leonidas Oliveira**
