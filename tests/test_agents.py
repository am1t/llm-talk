"""Tests for AIAgent."""

from unittest.mock import MagicMock, patch

from llm_talk.agents import AIAgent


def _make_agent(system_prompt="You are a test agent.") -> AIAgent:
    client = MagicMock()
    return AIAgent(name="TestAgent", model="openai:gpt-4o-mini", system_prompt=system_prompt, client=client)


def test_agent_initializes_with_system_prompt():
    agent = _make_agent("Hello system.")
    assert agent.messages == [{"role": "system", "content": "Hello system."}]


def test_add_user_message():
    agent = _make_agent()
    agent.add_user_message("hi there")
    assert agent.messages[-1] == {"role": "user", "content": "hi there"}


def test_add_assistant_message():
    agent = _make_agent()
    agent.add_assistant_message("response text")
    assert agent.messages[-1] == {"role": "assistant", "content": "response text"}


def test_respond_returns_content():
    agent = _make_agent()
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "Hello from mock!"
    agent.client.chat.completions.create.return_value = mock_response

    agent.add_user_message("Say hello.")
    result = agent.respond()

    assert result == "Hello from mock!"
    agent.client.chat.completions.create.assert_called_once_with(
        model="openai:gpt-4o-mini",
        messages=agent.messages,
        temperature=0.7,
    )


def test_respond_returns_error_string_on_failure():
    agent = _make_agent()
    agent.client.chat.completions.create.side_effect = RuntimeError("network down")

    result = agent.respond()

    assert result == "[TestAgent could not generate a response]"


def test_client_created_if_not_provided():
    with patch("llm_talk.agents.aisuite.Client") as mock_client_cls:
        agent = AIAgent(name="A", model="openai:gpt-4o-mini", system_prompt="sys")
        mock_client_cls.assert_called_once()
        assert agent.client is mock_client_cls.return_value
