import os
from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str = "") -> list[str]:
    raw = os.getenv(name, default)
    return [v.strip() for v in raw.split(",") if v.strip()]

# ---------------------------------------------------------------------------
# Gemini (Google)
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")

# ---------------------------------------------------------------------------
# OpenRouter (fallback — any model via openrouter.ai)
# OPENROUTER_MODELS is a comma-separated priority list; the provider tries
# each in order and moves to the next on a rate-limit error.
# Any model slug from https://openrouter.ai/models is valid.
# ---------------------------------------------------------------------------
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODELS: list[str] = _csv_env("OPENROUTER_MODELS", "google/gemini-flash-1.5")

# Model tier presets (can be overridden in .env)
SMALL_MODEL = os.getenv("SMALL_MODEL", "mistralai/mistral-7b-instruct")
MEDIUM_MODEL = os.getenv("MEDIUM_MODEL", "mistralai/mixtral-8x22b-instruct")
LARGE_MODEL = os.getenv("LARGE_MODEL", "nousresearch/hermes-3-llama-3.1-405b")

# Tier-associated backup models (comma-separated env vars)
SMALL_MODEL_BACKUPS: list[str] = _csv_env("SMALL_MODEL_BACKUPS")
MEDIUM_MODEL_BACKUPS: list[str] = _csv_env("MEDIUM_MODEL_BACKUPS")
LARGE_MODEL_BACKUPS: list[str] = _csv_env("LARGE_MODEL_BACKUPS")

# ---------------------------------------------------------------------------
# LLM provider routing
# Primary provider is tried first; fallbacks are tried in order on rate limits.
# Valid values: "gemini", "openrouter"
# ---------------------------------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_FALLBACK_PROVIDERS: list[str] = _csv_env("LLM_FALLBACK_PROVIDERS", "openrouter")
LLM_ROUTING_DEBUG = os.getenv("LLM_ROUTING_DEBUG", "false").lower() in {"1", "true", "yes", "on"}

# Context caching settings
# Note: Context caching requires a paid API tier. Set to False if using free tier.
ENABLE_CONTEXT_CACHING = os.getenv("ENABLE_CONTEXT_CACHING", "false").lower() in {"1", "true", "yes", "on"}
CACHE_TTL_HOURS = 1

# Temperature settings (balanced for both narrative and state updates)
TEMPERATURE = 0.6

# Context retrieval optimization
SELECTIVE_CONTEXT_LOADING = True

# Server settings
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Session settings
SESSION_CODE_LENGTH = 6
SESSION_TIMEOUT_HOURS = 24
MAX_PLAYERS_PER_SESSION = 8

# Character color palette (Homestuck-style)
CHARACTER_COLORS = [
    "#0715cd",  # Blue (John/EB)
    "#e00707",  # Red (Dave/TG)
    "#4ac925",  # Green (Jade/GG)
    "#a2069d",  # Purple (Rose/TT)
    "#a10000",  # Maroon (Karkat)
    "#a1a100",  # Olive (Sollux)
    "#416600",  # Lime (Nepeta)
    "#005682",  # Teal (Vriska)
]
