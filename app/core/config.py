from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Production RAG Summarizer"
    LLAMA_CLOUD_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()