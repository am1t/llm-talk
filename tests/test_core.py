"""Tests for Interview and InterviewResult."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch


from llm_talk.core import Interview, InterviewResult
from llm_talk.templates import TopicTemplate


# ---------------------------------------------------------------------------
# InterviewResult
# ---------------------------------------------------------------------------


def _make_result(**kwargs) -> InterviewResult:
    defaults = dict(
        evaluation="Good conversation.",
        conversation=[
            {"turn": 1, "agent": "Interviewer", "response": "Hello!"},
            {"turn": 2, "agent": "Interviewee", "response": "Hi there!"},
        ],
        total_turns=2,
        loop_detected=False,
        loop_reason="",
        interviewer_name="Interviewer",
        interviewee_name="Interviewee",
        evaluator_model="anthropic:claude-sonnet-4-5",
    )
    defaults.update(kwargs)
    return InterviewResult(**defaults)


def test_interview_result_to_dict():
    result = _make_result()
    d = result.to_dict()
    assert d["evaluation"] == "Good conversation."
    assert d["total_turns"] == 2
    assert d["loop_detected"] is False
    assert d["interviewer_name"] == "Interviewer"
    assert d["interviewee_name"] == "Interviewee"
    assert d["evaluator_model"] == "anthropic:claude-sonnet-4-5"
    assert len(d["conversation"]) == 2


def test_interview_result_str():
    result = _make_result(evaluation="Excellent!")
    assert str(result) == "Excellent!"


def test_interview_result_save_generates_filename():
    result = _make_result()
    with tempfile.TemporaryDirectory() as tmpdir:
        original_cwd = Path.cwd()
        import os
        os.chdir(tmpdir)
        try:
            path = result.save()
            assert Path(path).name.startswith("interview_")
            assert path.endswith(".md")
            assert Path(path).exists()
        finally:
            os.chdir(original_cwd)


def test_interview_result_save_explicit_path():
    result = _make_result()
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp_path = f.name

    returned = result.save(tmp_path)
    assert returned == tmp_path
    content = Path(tmp_path).read_text(encoding="utf-8")
    assert "Hello!" in content
    assert "Hi there!" in content
    assert "Good conversation." in content


# ---------------------------------------------------------------------------
# Interview initialisation
# ---------------------------------------------------------------------------


def test_interview_resolves_models():
    iv = Interview("openai", "claude", evaluator="openai")
    assert iv.interviewer_model == "openai:gpt-4o-mini"
    assert iv.interviewee_model == "anthropic:claude-sonnet-4-5"
    assert iv.evaluator_model == "openai:gpt-4o-mini"


def test_interview_default_topics():
    iv = Interview("openai", "claude")
    assert iv.topics == TopicTemplate.DEFAULT


def test_interview_topics_string():
    iv = Interview("openai", "claude", topics="Just one topic")
    assert iv.topics == ["Just one topic"]


def test_interview_topics_list():
    iv = Interview("openai", "claude", topics=["topic A", "topic B"])
    assert iv.topics == ["topic A", "topic B"]


def test_interview_custom_prompts_stored():
    iv = Interview(
        "openai",
        "claude",
        evaluator_system_prompt="sys",
        evaluator_user_prompt="user",
        interviewer_system_prompt="ivr",
        interviewee_system_prompt="ivee",
    )
    assert iv.evaluator_system_prompt == "sys"
    assert iv.evaluator_user_prompt == "user"
    assert iv.interviewer_system_prompt == "ivr"
    assert iv.interviewee_system_prompt == "ivee"


# ---------------------------------------------------------------------------
# Interview.run() — integration with mocked API
# ---------------------------------------------------------------------------


def _mock_agent_respond(responses):
    """Return a side_effect list suitable for patching AIAgent.respond."""
    return responses


@patch("llm_talk.core.get_evaluation", return_value="Mocked evaluation.")
@patch("llm_talk.core.AIAgent")
def test_interview_run_returns_result(mock_agent_cls, mock_eval):
    # Each AIAgent instance alternates as interviewer / interviewee
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Interviewer question"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "Interviewee answer"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    result = Interview("openai", "claude").run(turns=4, verbose=False)

    assert isinstance(result, InterviewResult)
    assert result.total_turns == 4
    assert result.evaluation == "Mocked evaluation."
    assert result.interviewer_name == "OpenAI gpt-4o-mini"
    assert result.interviewee_name == "Anthropic claude-sonnet-4-5"
    assert result.loop_detected is False


@patch("llm_talk.core.get_evaluation", return_value="eval")
@patch("llm_talk.core.AIAgent")
def test_interview_run_conversation_structure(mock_agent_cls, mock_eval):
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Q"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "A"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    result = Interview("openai", "claude").run(turns=4, verbose=False)

    agents = [t["agent"] for t in result.conversation]
    assert agents[0] == "OpenAI gpt-4o-mini"
    assert agents[1] == "Anthropic claude-sonnet-4-5"
    assert agents[2] == "OpenAI gpt-4o-mini"
    assert agents[3] == "Anthropic claude-sonnet-4-5"


@patch("llm_talk.core.get_evaluation", return_value="eval")
@patch("llm_talk.core.detect_conversation_loop")
@patch("llm_talk.core.AIAgent")
def test_interview_run_stops_on_loop(mock_agent_cls, mock_detect, mock_eval):
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Q"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "A"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    # Return loop detected on the 11th turn check (turn index 10)
    mock_detect.return_value = (True, "farewell loop detected")

    result = Interview("openai", "claude").run(turns=20, verbose=False)

    # Should stop after 11 turns (loop is checked starting at turn index 10)
    assert result.total_turns == 11
    assert result.loop_detected is True
    assert result.loop_reason == "farewell loop detected"


@patch("llm_talk.core.get_evaluation", return_value="eval")
@patch("llm_talk.core.AIAgent")
def test_interview_run_uses_custom_system_prompts(mock_agent_cls, mock_eval):
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Q"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "A"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    Interview(
        "openai",
        "claude",
        interviewer_system_prompt="custom ivr prompt",
        interviewee_system_prompt="custom ivee prompt",
    ).run(turns=2, verbose=False)

    # First AIAgent call should use the custom interviewer prompt
    first_call_kwargs = mock_agent_cls.call_args_list[0].kwargs
    assert first_call_kwargs["system_prompt"] == "custom ivr prompt"

    # Second AIAgent call should use the custom interviewee prompt
    second_call_kwargs = mock_agent_cls.call_args_list[1].kwargs
    assert second_call_kwargs["system_prompt"] == "custom ivee prompt"


# ---------------------------------------------------------------------------
# InterviewResult — None evaluation (deferred)
# ---------------------------------------------------------------------------


def test_interview_result_str_no_evaluation():
    result = _make_result(evaluation=None)
    assert ".evaluate()" in str(result)


def test_interview_result_to_dict_no_evaluation():
    result = _make_result(evaluation=None)
    assert result.to_dict()["evaluation"] is None


def test_interview_result_save_with_no_evaluation():
    result = _make_result(evaluation=None)
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        tmp_path = f.name

    result.save(tmp_path)
    content = Path(tmp_path).read_text(encoding="utf-8")
    assert "Evaluation not yet run" in content
    assert "None" not in content


def test_interview_result_evaluate_method():
    result = _make_result(evaluation=None)
    result._topics = ["topic A"]

    with patch("llm_talk.core.get_evaluation", return_value="Deferred evaluation.") as mock_eval:
        returned = result.evaluate()

    assert returned == "Deferred evaluation."
    assert result.evaluation == "Deferred evaluation."
    mock_eval.assert_called_once_with(
        result.conversation,
        result.interviewer_name,
        result.interviewee_name,
        evaluator_model=result.evaluator_model,
        topics=["topic A"],
        evaluation_dimensions=None,
        evaluator_system_prompt=None,
        evaluator_user_prompt=None,
    )


def test_interview_result_evaluate_idempotent():
    result = _make_result(evaluation=None)

    with patch("llm_talk.core.get_evaluation", return_value="Cached eval.") as mock_eval:
        result.evaluate()
        result.evaluate()  # second call

    assert mock_eval.call_count == 1
    assert result.evaluation == "Cached eval."


def test_interview_result_evaluate_when_already_populated():
    result = _make_result(evaluation="Already evaluated.")
    with patch("llm_talk.core.get_evaluation") as mock_eval:
        returned = result.evaluate()

    assert returned == "Already evaluated."
    mock_eval.assert_not_called()


# ---------------------------------------------------------------------------
# Interview.run() — evaluate=False
# ---------------------------------------------------------------------------


@patch("llm_talk.core.get_evaluation", return_value="Should not be called")
@patch("llm_talk.core.AIAgent")
def test_interview_run_evaluate_false(mock_agent_cls, mock_eval):
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Q"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "A"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    result = Interview("openai", "claude").run(turns=2, verbose=False, evaluate=False)

    assert result.evaluation is None
    mock_eval.assert_not_called()


@patch("llm_talk.core.get_evaluation", return_value="Deferred!")
@patch("llm_talk.core.AIAgent")
def test_interview_run_evaluate_false_then_deferred(mock_agent_cls, mock_eval):
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Q"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "A"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    result = Interview("openai", "claude").run(turns=2, verbose=False, evaluate=False)
    assert result.evaluation is None

    text = result.evaluate()
    assert text == "Deferred!"
    assert result.evaluation == "Deferred!"
    mock_eval.assert_called_once()


@patch("llm_talk.core.get_evaluation", return_value="eval")
@patch("llm_talk.core.AIAgent")
def test_interview_run_private_fields_populated(mock_agent_cls, mock_eval):
    interviewer = MagicMock()
    interviewer.name = "OpenAI gpt-4o-mini"
    interviewer.respond.return_value = "Q"

    interviewee = MagicMock()
    interviewee.name = "Anthropic claude-sonnet-4-5"
    interviewee.respond.return_value = "A"

    mock_agent_cls.side_effect = [interviewer, interviewee]

    result = Interview(
        "openai",
        "claude",
        topics=["topic X"],
        evaluator_system_prompt="custom sys",
    ).run(turns=2, verbose=False, evaluate=False)

    assert result._topics == ["topic X"]
    assert result._evaluator_system_prompt == "custom sys"
    assert result._evaluation_dimensions is None
    assert result._evaluator_user_prompt is None
