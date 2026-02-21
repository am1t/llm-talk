"""Tests for conversation evaluation."""

from unittest.mock import MagicMock, patch

from llm_talk.evaluators import get_evaluation
from llm_talk.templates import EvaluatorTemplate


SAMPLE_TURNS = [
    {"turn": 1, "agent": "OpenAI GPT", "response": "Hello, tell me about yourself."},
    {"turn": 2, "agent": "Claude", "response": "I'm an AI assistant by Anthropic."},
    {"turn": 3, "agent": "OpenAI GPT", "response": "What are your limitations?"},
    {"turn": 4, "agent": "Claude", "response": "I can struggle with real-time data."},
]


def _mock_client(text="Great conversation overall."):
    client = MagicMock()
    client.chat.completions.create.return_value.choices[0].message.content = text
    return client


def test_get_evaluation_returns_string():
    with patch("llm_talk.evaluators.aisuite.Client", return_value=_mock_client()):
        result = get_evaluation(SAMPLE_TURNS, "OpenAI GPT", "Claude")
    assert isinstance(result, str)
    assert len(result) > 0


def test_get_evaluation_uses_custom_user_prompt():
    client = _mock_client("custom result")
    with patch("llm_talk.evaluators.aisuite.Client", return_value=client):
        result = get_evaluation(
            SAMPLE_TURNS,
            "OpenAI GPT",
            "Claude",
            evaluator_user_prompt="Evaluate this: <transcript>",
        )

    assert result == "custom result"
    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert user_msg["content"] == "Evaluate this: <transcript>"


def test_get_evaluation_with_topics():
    client = _mock_client()
    with patch("llm_talk.evaluators.aisuite.Client", return_value=client):
        get_evaluation(
            SAMPLE_TURNS,
            "OpenAI GPT",
            "Claude",
            topics=["reasoning", "creativity"],
        )

    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "reasoning" in user_msg["content"]
    assert "creativity" in user_msg["content"]


def test_get_evaluation_with_custom_dimensions():
    client = _mock_client()
    with patch("llm_talk.evaluators.aisuite.Client", return_value=client):
        get_evaluation(
            SAMPLE_TURNS,
            "OpenAI GPT",
            "Claude",
            evaluation_dimensions=["**Humor**: Was it funny?"],
        )

    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "Humor" in user_msg["content"]


def test_get_evaluation_with_custom_system_prompt():
    client = _mock_client()
    with patch("llm_talk.evaluators.aisuite.Client", return_value=client):
        get_evaluation(
            SAMPLE_TURNS,
            "OpenAI GPT",
            "Claude",
            evaluator_system_prompt="You are a strict critic.",
        )

    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    sys_msg = next(m for m in messages if m["role"] == "system")
    assert sys_msg["content"] == "You are a strict critic."


def test_get_evaluation_default_system_prompt():
    client = _mock_client()
    with patch("llm_talk.evaluators.aisuite.Client", return_value=client):
        get_evaluation(SAMPLE_TURNS, "OpenAI GPT", "Claude")

    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    sys_msg = next(m for m in messages if m["role"] == "system")
    assert sys_msg["content"] == EvaluatorTemplate.DEFAULT_SYSTEM


def test_get_evaluation_transcript_included():
    client = _mock_client()
    with patch("llm_talk.evaluators.aisuite.Client", return_value=client):
        get_evaluation(SAMPLE_TURNS, "OpenAI GPT", "Claude")

    call_args = client.chat.completions.create.call_args
    messages = call_args.kwargs["messages"]
    user_msg = next(m for m in messages if m["role"] == "user")
    assert "tell me about yourself" in user_msg["content"]
    assert "real-time data" in user_msg["content"]
