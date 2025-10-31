from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # FastAPI
    swagger_servers_list: Optional[str] = None

    # Gemini
    gemini_api_key: str
    gemini_model: str

    # MCP Server
    mcp_server_url: str
    mcp_server_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
