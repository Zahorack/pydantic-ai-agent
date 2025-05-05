from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o"
    temperature: float = 0.0
    searxng_url: str = "http://localhost:8080"
    storage_dir: Path = Path(__file__).parent / "storage"
    max_download_retries: int = 3
    timeout: int = 5
    log_level: str = "INFO"
    urllib_log_level: str = "INFO"
    openai_log_level: str = "DEBUG"
    logfire_token: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",
    )

    @field_validator("storage_dir")
    @classmethod
    def create_storage_dir(cls, v: Path) -> Path:
        v.mkdir(parents=True, exist_ok=True)
        return v


settings = Settings()
