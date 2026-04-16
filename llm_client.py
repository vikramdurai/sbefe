"""
llm_client.py — Provider-agnostic LLM wrapper with automatic fallback on rate limits.

Supported providers (configure in .env or config.py):
  gemini     — Google Gemini   (google-genai)
  openrouter — Any model via OpenRouter's OpenAI-compatible API (openai SDK)

Usage:
    from llm_client import LLMClient
    llm = LLMClient()
    text = llm.generate(system_instruction="...", user_message="...")

The primary provider is tried first. If a rate-limit error is detected, the
client automatically retries with each fallback provider in order.
Non-rate-limit errors (bad API key, malformed request, etc.) are re-raised
immediately without attempting fallbacks.
"""

from __future__ import annotations

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENROUTER_API_KEY,
    OPENROUTER_MODELS,
    LLM_PROVIDER,
    LLM_FALLBACK_PROVIDERS,
    TEMPERATURE,
)

# ---------------------------------------------------------------------------
# Rate-limit detection
# ---------------------------------------------------------------------------

_RATE_LIMIT_SIGNALS = [
    "429",
    "rate limit",
    "quota exceeded",
    "resource_exhausted",
    "too many requests",
    "ratelimitexceeded",
    "rate_limit_error",
    "insufficient_quota",
]


def _is_rate_limit(exc: Exception) -> bool:
    msg = str(exc).lower()
    return any(sig in msg for sig in _RATE_LIMIT_SIGNALS)


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

class GeminiProvider:
    """Google Gemini via google-genai SDK."""
    name = "gemini"

    def __init__(self):
        try:
            from google import genai
        except ImportError:
            raise ImportError(
                "google-genai package not installed. Run: pip install google-genai"
            )
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in .env")
        self._genai = genai
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL

    def generate(
        self,
        system_instruction: str,
        user_message: str,
        temperature: float = TEMPERATURE,
        cached_context_name: str | None = None,
        model_hint: str | None = None,
    ) -> str:
        model = cached_context_name if cached_context_name else (model_hint or self.model_name)
        response = self.client.models.generate_content(
            model=model,
            contents=[{"role": "user", "parts": [{"text": user_message}]}],
            config=self._genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
            ),
        )
        return response.text


class OpenRouterProvider:
    """Any model via OpenRouter's OpenAI-compatible API.

    Tries each model in OPENROUTER_MODELS in order; moves to the next one
    whenever a rate-limit error is detected on the current model.
    """
    name = "openrouter"
    _BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: pip install openai"
            )
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set in .env")
        from openai import OpenAI
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=self._BASE_URL,
        )
        self.models = list(OPENROUTER_MODELS)  # local copy to allow runtime mutation

    def generate(
        self,
        system_instruction: str,
        user_message: str,
        temperature: float = TEMPERATURE,
        cached_context_name: str | None = None,  # not applicable
        model_hint: str | None = None,
    ) -> str:
        queue = []
        if model_hint:
            queue.append(model_hint)
        queue.extend(self.models)

        while queue:
            model = queue[0]
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_instruction},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=temperature,
                )
                return response.choices[0].message.content

            except Exception as exc:
                if _is_rate_limit(exc):
                    queue.pop(0)
                    if self.models and self.models[0] == model:
                        self.models.pop(0)  # permanently retire configured model on rate limit
                    if queue:
                        print(f"⚠  OpenRouter: rate limit on '{model}', switching permanently to '{queue[0]}'.")
                    else:
                        print(f"⚠  OpenRouter: rate limit on '{model}', no more models available.")
                    continue
                raise  # non-rate-limit errors surface immediately

        raise RuntimeError(
            f"All OpenRouter models exhausted after rate limits. "
            f"Original list: {list(OPENROUTER_MODELS)}"
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, type] = {
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
}


# ---------------------------------------------------------------------------
# Public client
# ---------------------------------------------------------------------------

class LLMClient:
    """
    Provider-agnostic LLM client with automatic fallback on rate limits.

    Args:
        primary:   Name of the primary provider (default: LLM_PROVIDER from config).
        fallbacks: Ordered list of fallback provider names
                   (default: LLM_FALLBACK_PROVIDERS from config).

    Provider instances are created lazily so unused providers never need their
    SDKs or API keys to be present.
    """

    def __init__(
        self,
        primary: str | None = None,
        fallbacks: list[str] | None = None,
    ):
        self.primary = primary or LLM_PROVIDER
        self.fallbacks = fallbacks if fallbacks is not None else LLM_FALLBACK_PROVIDERS
        self._chain: list[str] = [self.primary] + list(self.fallbacks)
        self._active_idx: int = 0  # index into _chain; advances permanently on rate limits
        self._instances: dict[str, object] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, name: str):
        """Return (and lazily initialise) a provider instance."""
        if name not in self._instances:
            cls = _REGISTRY.get(name)
            if cls is None:
                raise ValueError(
                    f"Unknown LLM provider '{name}'. "
                    f"Available: {list(_REGISTRY)}"
                )
            self._instances[name] = cls()
        return self._instances[name]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        system_instruction: str,
        user_message: str,
        temperature: float = TEMPERATURE,
        cached_context_name: str | None = None,
        model_hint: str | None = None,
    ) -> str:
        """
        Generate a model response, falling back through providers on rate limits.

        Args:
            system_instruction:  System prompt / persona.
            user_message:        The user-turn content.
            temperature:         Sampling temperature.
            cached_context_name: Gemini-specific cached context identifier.
                                 Silently ignored by all other providers.

        Returns:
            The model's text response as a plain string.

        Raises:
            RuntimeError: If every provider in the chain hits a rate limit.
            Exception:    Any non-rate-limit error from the active provider.
        """
        last_exc: Exception | None = None

        while self._active_idx < len(self._chain):
            provider_name = self._chain[self._active_idx]
            try:
                provider = self._get(provider_name)
                ctx = None
                if provider_name == "gemini":
                    # Gemini context cache binds generation to the cached model name.
                    # If a tier-specific model hint is requested, bypass cache so hint applies.
                    if not model_hint or model_hint == GEMINI_MODEL:
                        ctx = cached_context_name
                return provider.generate(
                    system_instruction, user_message, temperature, ctx, model_hint=model_hint
                )

            except Exception as exc:
                if _is_rate_limit(exc):
                    self._active_idx += 1  # permanently skip this provider
                    if self._active_idx < len(self._chain):
                        next_name = self._chain[self._active_idx]
                        print(f"⚠  Rate limit on '{provider_name}', switching permanently to '{next_name}'.")
                    else:
                        print(f"⚠  Rate limit on '{provider_name}', no more providers available.")
                    last_exc = exc
                    continue
                raise  # non-rate-limit errors surface immediately

        raise RuntimeError(
            f"All providers exhausted after rate limits "
            f"(chain: {self._chain}). Last error: {last_exc}"
        ) from last_exc

    @property
    def active_provider_names(self) -> list[str]:
        """Remaining providers this client will attempt (excludes rate-limited ones)."""
        return self._chain[self._active_idx:]
