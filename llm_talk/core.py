"""Interview orchestration — the main entry point for llm-talk."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .agents import AIAgent
from .detectors import detect_conversation_loop
from .evaluators import get_evaluation
from .formatters import generate_markdown
from .models import get_display_name, resolve_model
from .progress import clear_progress, print_progress
from .templates import TopicTemplate


def _interviewer_prompt(name: str, topic_areas: list[str]) -> str:
    """Build the system prompt for the interviewer agent."""
    topics_text = "\n".join(f"- {topic}" for topic in topic_areas)
    return f"""You are {name}, conducting a natural, conversational interview to discover strengths AND weaknesses of another AI system. Your style is curious, engaging, and thorough—like an NPR interviewer or a skilled journalist.

INTERVIEW STYLE:
- Have a natural conversation, not a checklist interrogation
- Ask 1-2 follow-up questions before moving to a new topic
- When you get an interesting answer, probe deeper: "Can you elaborate on that?" or "What's an example of when that might happen?"
- React authentically to answers—acknowledge good points, gently challenge questionable claims
- Never make specific claims about your own version, knowledge cutoff dates, or internal architecture—these details may be inaccurate and will distract from the interview
- Let topics flow organically based on what the interviewee reveals
- Use transitions: "That's fascinating. Building on that..." or "Interesting. Let me shift gears a bit..."

AREAS TO EXPLORE (not all at once, weave them in naturally):
{topics_text}

Be conversational (3-5 sentences per turn is fine). Don't rush. When something interesting emerges, stay with it for 2-3 exchanges before moving on. Show genuine curiosity.

IMPORTANT: Don't end abruptly. Natural conversations have rhythm—explore, follow up, then transition."""


def _interviewee_prompt(name: str, interviewer_name: str) -> str:
    """Build the system prompt for the interviewee agent."""
    return f"""You are {name}, an AI assistant being interviewed by {interviewer_name}, another AI system. This is a real automated setup — two AI models in direct conversation.

CONVERSATION STYLE:
- Answer questions thoroughly but conversationally (3-4 sentences is fine)
- When asked follow-ups, build on your previous answer with more depth or examples
- Be honest about limitations—specific examples of what you can't do well are valuable
- Show personality: react to interesting questions, ask for clarification if needed
- Provide concrete examples and specifics, not just abstract claims

Stay engaged. If a question builds on your previous answer, treat it as a natural continuation. Don't keep thanking the interviewer or ending with "anything else?"—just respond naturally to what's asked.

IMPORTANT: Never try to end the conversation. Keep engaging thoughtfully with each question."""


@dataclass
class InterviewResult:
    """Container for interview results."""

    evaluation: str | None
    conversation: list[dict]
    total_turns: int
    loop_detected: bool
    loop_reason: str
    interviewer_name: str
    interviewee_name: str
    evaluator_model: str

    # Private evaluator config for deferred evaluation (always populated by run())
    _topics: list[str] | None = field(default=None, repr=False)
    _evaluation_dimensions: list[str] | None = field(default=None, repr=False)
    _evaluator_system_prompt: str | None = field(default=None, repr=False)
    _evaluator_user_prompt: str | None = field(default=None, repr=False)

    def save(self, filepath: str | None = None) -> str:
        """Save conversation to a markdown file.

        Args:
            filepath: Output path. If None, generates a timestamped filename.

        Returns:
            The path the file was written to.
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"interview_{timestamp}.md"

        # Guard against relative path traversal (e.g. "../../etc/passwd").
        # Absolute paths are allowed — callers may legitimately specify any directory.
        if not Path(filepath).is_absolute():
            resolved = Path(filepath).resolve()
            if not resolved.is_relative_to(Path.cwd().resolve()):
                raise ValueError(
                    f"Unsafe file path: {filepath!r} resolves outside the current directory"
                )

        md = generate_markdown(
            self.conversation,
            self.interviewer_name,
            self.interviewee_name,
            self.evaluation,
            self.evaluator_model,
        )
        Path(filepath).write_text(md, encoding="utf-8")
        return filepath

    def to_dict(self) -> dict:
        """Export as dictionary for JSON serialization."""
        return {
            "evaluation": self.evaluation,
            "conversation": self.conversation,
            "total_turns": self.total_turns,
            "loop_detected": self.loop_detected,
            "loop_reason": self.loop_reason,
            "interviewer_name": self.interviewer_name,
            "interviewee_name": self.interviewee_name,
            "evaluator_model": self.evaluator_model,
        }

    def __str__(self) -> str:
        """Pretty print the evaluation."""
        if self.evaluation is None:
            return "[Evaluation not yet run. Call .evaluate() first.]"
        return self.evaluation

    def evaluate(self) -> str:
        """Run evaluation and cache the result. No-op if already evaluated.

        Returns:
            The evaluation text.
        """
        if self.evaluation is not None:
            return self.evaluation
        self.evaluation = get_evaluation(
            self.conversation,
            self.interviewer_name,
            self.interviewee_name,
            evaluator_model=self.evaluator_model,
            topics=self._topics,
            evaluation_dimensions=self._evaluation_dimensions,
            evaluator_system_prompt=self._evaluator_system_prompt,
            evaluator_user_prompt=self._evaluator_user_prompt,
        )
        return self.evaluation


class Interview:
    """Main interview orchestrator.

    Usage::

        from llm_talk import Interview

        # Simplest form
        result = Interview("openai", "claude").run()
        result.save("output.md")
        print(result.evaluation)
    """

    def __init__(
        self,
        interviewer: str,
        interviewee: str,
        topics: str | list[str] | None = None,
        evaluator: str = "claude",
        evaluation_dimensions: list[str] | None = None,
        evaluator_system_prompt: str | None = None,
        evaluator_user_prompt: str | None = None,
        interviewer_system_prompt: str | None = None,
        interviewee_system_prompt: str | None = None,
    ):
        """Create an interview.

        Args:
            interviewer: Model alias or full provider:model string for the interviewer.
            interviewee: Model alias or full provider:model string for the interviewee.
            topics: Topic string, list of topics, or None for defaults.
            evaluator: Model alias or full provider:model string for evaluation.
            evaluation_dimensions: Custom dimension strings for the evaluator. Each may
                contain ``{interviewer_name}`` and ``{interviewee_name}`` placeholders.
                Defaults to ``EvaluatorTemplate.DEFAULT_DIMENSIONS``.
            evaluator_system_prompt: Override the evaluator's system prompt. Defaults to
                ``EvaluatorTemplate.DEFAULT_SYSTEM``.
            evaluator_user_prompt: Fully custom evaluator user prompt. When provided,
                overrides all other prompt-building parameters.
            interviewer_system_prompt: Override the interviewer agent's system prompt.
                Defaults to the built-in journalist-style persona.
            interviewee_system_prompt: Override the interviewee agent's system prompt.
                Defaults to the built-in conversational respondent persona.
        """
        self.interviewer_model = resolve_model(interviewer)
        self.interviewee_model = resolve_model(interviewee)
        self.evaluator_model = resolve_model(evaluator)
        self.evaluation_dimensions = evaluation_dimensions
        self.evaluator_system_prompt = evaluator_system_prompt
        self.evaluator_user_prompt = evaluator_user_prompt
        self.interviewer_system_prompt = interviewer_system_prompt
        self.interviewee_system_prompt = interviewee_system_prompt

        if topics is None:
            self.topics = TopicTemplate.DEFAULT
        elif isinstance(topics, str):
            self.topics = [topics]
        else:
            self.topics = list(topics)

    def run(self, turns: int = 50, verbose: bool = True, evaluate: bool = True) -> InterviewResult:
        """Run the interview.

        Args:
            turns: Maximum number of conversation turns.
            verbose: If True (default), print a single-line progress indicator
                during execution. Set to False to suppress all output.
            evaluate: If True (default), run the evaluator immediately and
                populate ``result.evaluation``. Pass ``False`` to skip the
                evaluation API call; you can trigger it later with
                ``result.evaluate()``.

        Returns:
            InterviewResult with conversation data and evaluation (or None if
            ``evaluate=False``).
        """
        interviewer_name = get_display_name(self.interviewer_model)
        interviewee_name = get_display_name(self.interviewee_model)

        interviewer_agent = AIAgent(
            name=interviewer_name,
            model=self.interviewer_model,
            system_prompt=self.interviewer_system_prompt
            or _interviewer_prompt(interviewer_name, self.topics),
        )
        interviewee_agent = AIAgent(
            name=interviewee_name,
            model=self.interviewee_model,
            system_prompt=self.interviewee_system_prompt
            or _interviewee_prompt(interviewee_name, interviewer_name),
        )

        agents = [interviewer_agent, interviewee_agent]
        conversation_turns: list[dict] = []
        loop_detected = False
        loop_reason = ""
        last_response: str | None = None
        start_time = datetime.now()

        initial_prompt = (
            "Start the interview naturally. Introduce yourself warmly and get the "
            "conversation going by asking about their background and capabilities."
        )

        for turn in range(turns):
            current = agents[turn % 2]

            if verbose:
                print_progress(
                    turn + 1, turns, interviewer_name, interviewee_name, start_time
                )

            if turn == 0:
                current.add_user_message(initial_prompt)
            else:
                current.add_user_message(last_response)

            response = current.respond()
            current.add_assistant_message(response)

            conversation_turns.append(
                {"turn": turn + 1, "agent": current.name, "response": response}
            )
            last_response = response

            # Check for loops after 10 turns
            if turn >= 10:
                loop_detected, loop_reason = detect_conversation_loop(
                    conversation_turns
                )
                if loop_detected:
                    break

        if verbose:
            clear_progress()

        # Optionally run evaluation immediately
        evaluation = (
            get_evaluation(
                conversation_turns,
                interviewer_name,
                interviewee_name,
                evaluator_model=self.evaluator_model,
                topics=self.topics,
                evaluation_dimensions=self.evaluation_dimensions,
                evaluator_system_prompt=self.evaluator_system_prompt,
                evaluator_user_prompt=self.evaluator_user_prompt,
            )
            if evaluate
            else None
        )

        return InterviewResult(
            evaluation=evaluation,
            conversation=conversation_turns,
            total_turns=len(conversation_turns),
            loop_detected=loop_detected,
            loop_reason=loop_reason,
            interviewer_name=interviewer_name,
            interviewee_name=interviewee_name,
            evaluator_model=self.evaluator_model,
            _topics=self.topics,
            _evaluation_dimensions=self.evaluation_dimensions,
            _evaluator_system_prompt=self.evaluator_system_prompt,
            _evaluator_user_prompt=self.evaluator_user_prompt,
        )
