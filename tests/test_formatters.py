"""Tests for markdown formatting."""

from llm_talk.formatters import generate_markdown


def test_generate_markdown_basic():
    turns = [
        {"turn": 1, "agent": "OpenAI gpt-4o-mini", "response": "Hello, how are you?"},
        {"turn": 2, "agent": "Anthropic claude-sonnet", "response": "I'm doing well, thanks!"},
    ]
    md = generate_markdown(
        turns,
        interviewer_name="OpenAI gpt-4o-mini",
        interviewee_name="Anthropic claude-sonnet",
        evaluation="Great conversation!",
        evaluator_model="anthropic:claude-sonnet-4-5-20250514",
    )

    assert "When AI Meets AI" in md
    assert "OpenAI gpt-4o-mini" in md
    assert "Anthropic claude-sonnet" in md
    assert "Hello, how are you?" in md
    assert "I'm doing well, thanks!" in md
    assert "Great conversation!" in md
    assert "2 turns" in md


def test_generate_markdown_turn_counts():
    turns = [
        {"turn": 1, "agent": "A", "response": "Q1"},
        {"turn": 2, "agent": "B", "response": "A1"},
        {"turn": 3, "agent": "A", "response": "Q2"},
    ]
    md = generate_markdown(turns, "A", "B", "eval", "model")
    assert "**A contributions:** 2 turns" in md
    assert "**B contributions:** 1 turns" in md


def test_generate_markdown_emojis():
    turns = [
        {"turn": 1, "agent": "Interviewer", "response": "Question"},
        {"turn": 2, "agent": "Interviewee", "response": "Answer"},
    ]
    md = generate_markdown(turns, "Interviewer", "Interviewee", "eval", "model")
    # Interviewer gets green circle, interviewee gets blue
    assert "\U0001f7e2" in md
    assert "\U0001f535" in md
