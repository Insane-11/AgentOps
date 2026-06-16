from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AgentOps"
    debug: bool = False

    database_url: str = "postgresql+asyncpg://agentops:agentops@localhost:5432/agentops"
    database_url_sync: str = "postgresql://agentops:agentops@localhost:5432/agentops"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.1:8b"
    ollama_embedding_model: str = "nomic-embed-text"

    # LangFuse (self-hosted observability, optional)
    langfuse_secret_key: str = ""
    langfuse_public_key: str = ""
    langfuse_host: str = "http://localhost:3000"

    redis_url: str = ""

    allowed_origins: list[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"]

    app_url: str = "http://localhost:5174"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
