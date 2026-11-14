from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import error, request

from ...config import settings


class AIProviderError(RuntimeError):
    """Raised when the configured AI provider cannot answer a request."""


@dataclass(frozen=True)
class ChatResult:
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0


def _system_prompt(teaching_mode: str, context: dict[str, str]) -> str:
    context_text = "\n".join(f"- {key}: {value}" for key, value in context.items())
    return (
        "You are Learn2Code's personal programming tutor. Give accurate, "
        "guided explanations and never claim to have executed code. "
        f"Teaching mode: {teaching_mode}.\n"
        "Authenticated learning context:\n"
        f"{context_text or '- No additional context'}"
    )


def generate_reply(
    messages: list[dict[str, str]],
    teaching_mode: str,
    context: dict[str, str],
) -> ChatResult:
    if not settings.ai_provider_url or not settings.ai_provider_api_key:
        raise AIProviderError("AI provider is not configured. Set AI_PROVIDER_URL and AI_PROVIDER_API_KEY.")
    payload = json.dumps({
        "model": settings.ai_provider_model,
        "messages": [{"role": "system", "content": _system_prompt(teaching_mode, context)}, *messages],
        "max_tokens": settings.ai_max_tokens,
        "temperature": 0.2,
    }).encode()
    endpoint = settings.ai_provider_url.rstrip("/") + "/chat/completions"
    req = request.Request(
        endpoint,
        data=payload,
        headers={"Authorization": f"Bearer {settings.ai_provider_api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read())
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise AIProviderError("The AI provider is temporarily unavailable.") from exc
    try:
        choice = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise AIProviderError("The AI provider returned an invalid response.") from exc
    usage = data.get("usage") or {}
    return ChatResult(
        content=str(choice),
        prompt_tokens=int(usage.get("prompt_tokens", 0)),
        completion_tokens=int(usage.get("completion_tokens", 0)),
    )
