from fastapi import FastAPI
from app.api import api_router

app = FastAPI(
    title="User MCP Server Backend",
    description="Servidor Backend para realizar a comunicação entre o modelo 2.5 Flash do Google Gemini, o Frontend, com o intuito de usar o MCP",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(api_router)

@app.get('/', include_in_schema=False)
def root():
    return {'message': 'Enhanced FastAPI App'}
