from typing import TYPE_CHECKING, Any

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

if TYPE_CHECKING:
    from skills.utils.config import LLMConfig


def build_chat_model(cfg: "LLMConfig") -> BaseChatModel:
    """Создать chat-модель по LLMConfig.

    provider — имя интеграции LangChain ("openai", "anthropic", ...),
    model — имя модели БЕЗ litellm-префикса (например "gpt-4o-mini").
    """
    kwargs: dict[str, Any] = {
        "temperature": cfg.temperature,
        "max_tokens": cfg.max_tokens,
        "api_key": cfg.api_key,
    }
    if cfg.api_base:
        kwargs["base_url"] = cfg.api_base
    return init_chat_model(cfg.model, model_provider=cfg.provider, **kwargs)
