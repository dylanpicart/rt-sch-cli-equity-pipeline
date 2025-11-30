from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Snowflake
    SNOWFLAKE_ACCOUNT: Optional[str] = None
    SNOWFLAKE_USER: Optional[str] = None
    SNOWFLAKE_PASSWORD: Optional[str] = None
    SNOWFLAKE_WAREHOUSE: Optional[str] = None
    SNOWFLAKE_DATABASE: Optional[str] = "SCHOOL_CLIMATE"
    SNOWFLAKE_SCHEMA: Optional[str] = "GOLD"

    # OpenAI / embeddings
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-large"

    # Vector store
    VECTOR_BACKEND: str = "chroma"
    VECTOR_DIR: str = "./data/chroma_index"

    # Dev-mode flags
    USE_FAKE_EMBEDDINGS: bool = False
    USE_FAKE_LLM: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
