from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Production RAG Summarizer"
    
    LLAMA_CLOUD_API_KEY: str
    MONGO_URI: str
    MONGO_DB_NAME: str = "rag_summarizer"
    MONGO_COLLECTION_NAME: str = "documents"
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()