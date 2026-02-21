"""Tests for model resolution."""

from llm_talk.models import resolve_model, get_display_name


def test_resolve_known_alias():
    assert resolve_model("openai") == "openai:gpt-4o-mini"
    assert resolve_model("claude") == "anthropic:claude-sonnet-4-5"
    assert resolve_model("gpt4") == "openai:gpt-4o"


def test_resolve_passthrough():
    """Full provider:model strings should pass through unchanged."""
    assert resolve_model("openai:gpt-4o") == "openai:gpt-4o"
    assert resolve_model("anthropic:claude-opus-4-20250514") == "anthropic:claude-opus-4-20250514"


def test_resolve_unknown():
    """Unknown names should pass through unchanged."""
    assert resolve_model("some-future-model") == "some-future-model"


def test_display_name():
    assert get_display_name("openai:gpt-4o-mini") == "OpenAI gpt-4o-mini"
    assert get_display_name("anthropic:claude-sonnet-4-5-20250514") == "Anthropic claude-sonnet-4-5-20250514"
    assert get_display_name("google:gemini-2.0-flash") == "Google gemini-2.0-flash"


def test_display_name_unknown_provider():
    assert get_display_name("cohere:command-r") == "Cohere command-r"


def test_display_name_no_colon():
    """Should not crash on unresolved alias or typo — return input unchanged."""
    assert get_display_name("claud") == "claud"
