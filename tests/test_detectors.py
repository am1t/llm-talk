"""Tests for conversation loop detection."""

from llm_talk.detectors import detect_conversation_loop


def test_no_loop_short_conversation():
    turns = [{"agent": "A", "response": f"Message {i}"} for i in range(3)]
    detected, reason = detect_conversation_loop(turns)
    assert not detected
    assert reason == ""


def test_farewell_loop():
    turns = [
        {"agent": "A", "response": "Thank you, goodbye!"},
        {"agent": "B", "response": "Farewell, take care!"},
        {"agent": "A", "response": "Bye, see you later!"},
        {"agent": "B", "response": "Goodbye, it was nice talking!"},
        {"agent": "A", "response": "Take care, bye!"},
    ]
    detected, reason = detect_conversation_loop(turns)
    assert detected
    assert "goodbye" in reason.lower() or "farewell" in reason.lower()


def test_no_farewell_loop_normal_conversation():
    turns = [
        {"agent": "A", "response": "What are your thoughts on machine learning?"},
        {"agent": "B", "response": "I find it fascinating, especially deep learning approaches."},
        {"agent": "A", "response": "Can you elaborate on that?"},
        {"agent": "B", "response": "Sure, let me explain the key concepts."},
        {"agent": "A", "response": "That's very interesting, tell me more."},
    ]
    detected, reason = detect_conversation_loop(turns)
    assert not detected


def test_repetitive_short_responses():
    turns = [
        {"agent": "A", "response": "yes"},
        {"agent": "B", "response": "ok"},
        {"agent": "A", "response": "yes"},
        {"agent": "B", "response": "ok"},
        {"agent": "A", "response": "yes"},
    ]
    detected, reason = detect_conversation_loop(turns)
    assert detected
    assert "repetitive" in reason.lower()


def test_back_and_forth_pattern():
    base = "This is a fairly long response that repeats itself in the conversation loop test"
    turns = [
        {"agent": "A", "response": base + " from agent A first time"},
        {"agent": "B", "response": base + " from agent B first time"},
        {"agent": "A", "response": base + " from agent A first time"},
        {"agent": "B", "response": base + " from agent B first time"},
        {"agent": "A", "response": base + " from agent A first time"},
    ]
    detected, reason = detect_conversation_loop(turns)
    assert detected
    assert "back-and-forth" in reason.lower() or "repetitive" in reason.lower()
