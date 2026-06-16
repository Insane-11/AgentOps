from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AgentOps"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://agentops:agentops@localhost:5432/agentops"
    database_url_sync: str = "postgresql://agentops:agentops@localhost:5432/agentops"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    openai_api_key: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = "agentops"
    langsmith_endpoint: str = "https://api.smith.langchain.com"

    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
