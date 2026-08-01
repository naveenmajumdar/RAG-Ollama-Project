from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ollama_base_url: str = "http://localhost:11434"
    ollama_llm_model: str = "llama3.2"
    ollama_embed_model: str = "nomic-embed-text"

    chroma_persist_dir: str = "./chroma_db"

    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50

    chunk_size: int = 800
    chunk_overlap: int = 150

    top_k_retrieval: int = 5
    max_query_length: int = 1000

    log_level: str = "INFO"


settings = Settings()
