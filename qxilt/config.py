"""Configuration for Qxilt."""

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root: qxilt/config.py -> qxilt/ -> project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# QXILT_ENV=dev loads .env.local, QXILT_ENV=prod loads .env (default: prod)
_ENV = os.environ.get("QXILT_ENV", "prod")
_ENV_FILE = _PROJECT_ROOT / (".env.local" if _ENV == "dev" else ".env")


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE if _ENV_FILE.exists() else _PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        env_prefix="QXILT_",
        extra="ignore",
    )

    supabase_url: str = Field(
        ...,
        validation_alias="SUPABASE_URL",
        description="Supabase project URL (e.g. https://xxx.supabase.co or http://localhost:54321).",
    )
    supabase_service_role_key: str = Field(
        ...,
        validation_alias="SUPABASE_SERVICE_ROLE_KEY",
        description="Supabase service role key for server-side operations.",
    )
    beta_alpha: float = Field(
        default=5.0,
        description="Alpha parameter for Beta prior.",
    )
    beta_beta: float = Field(
        default=5.0,
        description="Beta parameter for Beta prior.",
    )
    confidence_level: float = Field(
        default=0.95,
        description="Confidence level for lower bound score (e.g. 0.95 for 95%%).",
    )
    api_base_url: str = Field(
        default="http://localhost:8000",
        description="Base URL for Qxilt API (used by CLI/SDK).",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
