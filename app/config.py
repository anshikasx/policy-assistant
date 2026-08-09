from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "policy-assistant"
    openrouter_api_key: str = ""
    llm_model: str = "google/gemini-2.0-flash-001"
    qdrant_url: str = "http://localhost:6333"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 5


settings = Settings()