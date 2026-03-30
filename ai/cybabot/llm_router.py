"""Multi-LLM Router for Cybabot Ultra.

Supports: Grok (xAI), Claude (Anthropic), DeepSeek, Gemini (Google), Ollama (local)
Each agent can be assigned its own LLM instance.
"""

from typing import Any
from langchain_core.language_models import BaseChatModel
import structlog

logger = structlog.get_logger()

# Available providers and their models
PROVIDERS = {
    "grok": {
        "models": ["grok-2-1212", "grok-2-vision-1212", "grok-beta"],
        "vision_models": ["grok-2-vision-1212"],
        "default": "grok-2-1212",
        "description": "xAI Grok - Fast and capable",
    },
    "claude": {
        "models": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        "vision_models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229"],
        "default": "claude-3-5-sonnet-20241022",
        "description": "Anthropic Claude - Best for reasoning",
    },
    "deepseek": {
        "models": ["deepseek-chat", "deepseek-coder"],
        "vision_models": [],
        "default": "deepseek-chat",
        "description": "DeepSeek - Excellent for code generation",
    },
    "gemini": {
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
        "vision_models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
        "default": "gemini-1.5-pro",
        "description": "Google Gemini - Large context window",
    },
    "ollama": {
        "models": ["llama3.2", "mistral", "codellama", "qwen2.5-coder"],
        "vision_models": ["llava"],
        "default": "llama3.2",
        "description": "Ollama - Local inference, no API key needed",
    },
}


class LLMRouter:
    """Routes LLM requests to the appropriate provider."""

    def __init__(self) -> None:
        self._settings: Any = None

    @property
    def settings(self) -> Any:
        if self._settings is None:
            from app.config import get_settings
            self._settings = get_settings()
        return self._settings

    def get_llm(
        self,
        provider: str,
        model: str | None = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> BaseChatModel:
        """Get a LangChain chat model for the specified provider."""
        provider = provider.lower()

        if provider not in PROVIDERS:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(PROVIDERS.keys())}")

        # Use default model if not specified
        if model is None:
            model = PROVIDERS[provider]["default"]

        logger.info("Creating LLM instance", provider=provider, model=model)

        if provider == "grok":
            return self._create_grok(model, temperature, **kwargs)
        elif provider == "claude":
            return self._create_claude(model, temperature, **kwargs)
        elif provider == "deepseek":
            return self._create_deepseek(model, temperature, **kwargs)
        elif provider == "gemini":
            return self._create_gemini(model, temperature, **kwargs)
        elif provider == "ollama":
            return self._create_ollama(model, temperature, **kwargs)
        else:
            raise ValueError(f"Provider not implemented: {provider}")

    def _create_grok(self, model: str, temperature: float, **kwargs: Any) -> BaseChatModel:
        """Create Grok (xAI) LLM instance."""
        from langchain_openai import ChatOpenAI

        if not self.settings.xai_api_key:
            raise ValueError("XAI_API_KEY not configured")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=self.settings.xai_api_key,
            base_url="https://api.x.ai/v1",
            **kwargs,
        )

    def _create_claude(self, model: str, temperature: float, **kwargs: Any) -> BaseChatModel:
        """Create Claude (Anthropic) LLM instance."""
        from langchain_anthropic import ChatAnthropic

        if not self.settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")

        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=self.settings.anthropic_api_key,
            **kwargs,
        )

    def _create_deepseek(self, model: str, temperature: float, **kwargs: Any) -> BaseChatModel:
        """Create DeepSeek LLM instance (OpenAI-compatible API)."""
        from langchain_openai import ChatOpenAI

        if not self.settings.deepseek_api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")

        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=self.settings.deepseek_api_key,
            base_url="https://api.deepseek.com/v1",
            **kwargs,
        )

    def _create_gemini(self, model: str, temperature: float, **kwargs: Any) -> BaseChatModel:
        """Create Gemini (Google) LLM instance."""
        from langchain_google_genai import ChatGoogleGenerativeAI

        if not self.settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY not configured")

        return ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=self.settings.google_api_key,
            **kwargs,
        )

    def _create_ollama(self, model: str, temperature: float, **kwargs: Any) -> BaseChatModel:
        """Create Ollama (local) LLM instance."""
        from langchain_community.chat_models import ChatOllama

        return ChatOllama(
            model=model,
            temperature=temperature,
            base_url=self.settings.ollama_base_url,
            **kwargs,
        )

    def get_available_providers(self) -> dict[str, Any]:
        """Get list of available providers with their status."""
        available = {}
        for provider, info in PROVIDERS.items():
            has_key = self._check_provider_key(provider)
            available[provider] = {
                **info,
                "available": has_key,
                "requires_key": provider != "ollama",
            }
        return available

    def _check_provider_key(self, provider: str) -> bool:
        """Check if a provider has its API key configured."""
        key_map = {
            "grok": self.settings.xai_api_key,
            "claude": self.settings.anthropic_api_key,
            "deepseek": self.settings.deepseek_api_key,
            "gemini": self.settings.google_api_key,
            "ollama": True,  # Always available (local)
        }
        return bool(key_map.get(provider))

    def get_best_available_provider(self) -> str:
        """Get the best available provider based on configured API keys."""
        priority = ["claude", "grok", "gemini", "deepseek", "ollama"]
        for provider in priority:
            if self._check_provider_key(provider):
                return provider
        return "ollama"  # Fallback to local


# Global router instance
llm_router = LLMRouter()
