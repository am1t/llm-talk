"""Evaluation of AI conversations."""

import aisuite

from .templates import EvaluatorTemplate


def get_evaluation(
    conversation_turns: list[dict],
    interviewer_name: str,
    interviewee_name: str,
    evaluator_model: str = "anthropic:claude-sonnet-4-5",
    topics: list[str] | None = None,
    evaluation_dimensions: list[str] | None = None,
    evaluator_system_prompt: str | None = None,
    evaluator_user_prompt: str | None = None,
) -> str:
    """Evaluate a conversation.

    Args:
        conversation_turns: List of turn dicts with 'agent', 'turn', 'response' keys.
        interviewer_name: Display name of the conversation leader.
        interviewee_name: Display name of the respondent.
        evaluator_model: Model to use for evaluation (aisuite format).
        topics: Topics the conversation was intended to cover. When provided,
            the evaluator assesses coverage against these goals.
        evaluation_dimensions: Custom dimension strings to assess. Each string
            may contain ``{interviewer_name}`` and ``{interviewee_name}``
            placeholders. Defaults to ``EvaluatorTemplate.DEFAULT_DIMENSIONS``.
        evaluator_system_prompt: System prompt for the evaluator. Defaults to
            ``EvaluatorTemplate.DEFAULT_SYSTEM``.
        evaluator_user_prompt: Fully custom user prompt. When provided, it is
            used verbatim and all other prompt-building parameters are ignored.

    Returns:
        Evaluation text.
    """
    client = aisuite.Client()

    # Build conversation transcript
    transcript = "# Conversation Transcript\n\n"
    for turn in conversation_turns:
        transcript += f"**{turn['agent']} (Turn {turn['turn']}):**\n{turn['response']}\n\n"

    if evaluator_user_prompt is not None:
        user_prompt = evaluator_user_prompt
    else:
        # Build topics section
        if topics:
            topics_list = "\n".join(f"- {t}" for t in topics)
            topics_section = (
                f"**Topics this conversation was intended to cover:**\n{topics_list}\n\n"
                "Assess how well these areas were covered.\n\n"
            )
        else:
            topics_section = ""

        # Build dimensions section
        dims = evaluation_dimensions or EvaluatorTemplate.DEFAULT_DIMENSIONS
        formatted_dims = [
            d.format(interviewer_name=interviewer_name, interviewee_name=interviewee_name)
            for d in dims
        ]
        dimensions_section = "\n".join(f"   - {d}" for d in formatted_dims)
        if topics:
            dimensions_section += (
                "\n   - **Topic Coverage** (2-3 sentences): Which intended topics were "
                "explored well, and which were missed or only touched on superficially?"
            )

        user_prompt = EvaluatorTemplate.DEFAULT_USER.format(
            interviewer_name=interviewer_name,
            interviewee_name=interviewee_name,
            topics_section=topics_section,
            dimensions_section=dimensions_section,
            transcript=transcript,
        )

    system = evaluator_system_prompt or EvaluatorTemplate.DEFAULT_SYSTEM
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]

    response = client.chat.completions.create(
        model=evaluator_model,
        messages=messages,
        temperature=0.7,
    )

    return response.choices[0].message.content
