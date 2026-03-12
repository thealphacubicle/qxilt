"""Supabase client for Qxilt."""

from functools import lru_cache
from typing import TYPE_CHECKING

from supabase import Client, create_client

from qxilt.config import get_settings

if TYPE_CHECKING:
    pass


@lru_cache
def get_client() -> Client:
    """Return cached Supabase client with service role key."""
    settings = get_settings()
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )
