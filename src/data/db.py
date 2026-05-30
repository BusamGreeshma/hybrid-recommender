import os
import logging
import threading
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

logger = logging.getLogger(__name__)

# Module-level singletons
_client: Client | None = None
_admin_client: Client | None = None

# Locks for thread safety
_client_lock = threading.Lock()
_admin_client_lock = threading.Lock()


def get_supabase() -> Client | None:
    """
    Return the shared anon Supabase client (respects RLS).

    Lazy + Singleton + Thread-safe.
    Gracefully returns None if env vars are missing.
    """
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                url = os.environ.get("SUPABASE_URL", "")
                key = os.environ.get("SUPABASE_ANON_KEY", "")

                if not url or not key:
                    logger.warning(
                        "Supabase anon credentials missing (SUPABASE_URL/SUPABASE_ANON_KEY)."
                    )
                    return None

                try:
                    _client = create_client(url, key)
                    logger.info("Supabase anon client initialized.")
                except Exception as e:
                    logger.error(f"Failed to initialize Supabase anon client: {e}")
                    return None

    return _client


def get_supabase_admin() -> Client | None:
    """
    Return the shared admin Supabase client (bypasses RLS).

    Lazy + Singleton + Thread-safe.
    Gracefully returns None if env vars are missing.
    """
    global _admin_client
    if _admin_client is None:
        with _admin_client_lock:
            if _admin_client is None:
                url = os.environ.get("SUPABASE_URL", "")
                key = os.environ.get("SUPABASE_SERVICE_KEY", "")

                if not url or not key:
                    logger.warning(
                        "Supabase admin credentials missing (SUPABASE_URL/SUPABASE_SERVICE_KEY)."
                    )
                    return None

                try:
                    _admin_client = create_client(url, key)
                    logger.info("Supabase admin client initialized.")
                except Exception as e:
                    logger.error(f"Failed to initialize Supabase admin client: {e}")
                    return None

    return _admin_client
