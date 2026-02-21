"""Model name resolution and aliases."""

MODEL_ALIASES = {
    "openai": "openai:gpt-4o-mini",
    "claude": "anthropic:claude-sonnet-4-5",
    "gpt4": "openai:gpt-4o",
    "gpt4-mini": "openai:gpt-4o-mini",
    "sonnet": "anthropic:claude-sonnet-4-5",
    "opus": "anthropic:claude-opus-4-5",
    "gemini": "google:gemini-2.0-flash",
    "mistral": "mistral:mistral-large-latest",
}


def resolve_model(name: str) -> str:
    """Convert short name to full provider:model format.

    Args:
        name: Short alias (e.g. "openai") or full name (e.g. "openai:gpt-4o")

    Returns:
        Full provider:model string for aisuite.
    """
    return MODEL_ALIASES.get(name, name)


def get_display_name(model: str) -> str:
    """Get a human-readable display name from a provider:model string.

    Args:
        model: Full provider:model string (e.g. "openai:gpt-4o-mini")

    Returns:
        Display name (e.g. "OpenAI GPT-4o-mini")
    """
    if ":" not in model:
        return model
    provider, model_name = model.split(":", 1)
    provider_names = {
        "openai": "OpenAI",
        "anthropic": "Anthropic",
        "google": "Google",
        "mistral": "Mistral",
    }
    display_provider = provider_names.get(provider, provider.title())
    return f"{display_provider} {model_name}"
