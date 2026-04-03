"""Environment-based AI configuration."""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NULLTHREAD_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_key: str | None = None
    llm_model: str = Field(default="claude-sonnet-4-20250514", validation_alias="MODEL")
    backend: str = "anthropic"  # anthropic | template
    cache_dir: str | None = None
