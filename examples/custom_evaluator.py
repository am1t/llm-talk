"""Custom evaluator example — controlling how the interview is assessed."""

from dotenv import load_dotenv
load_dotenv()

from llm_talk import Interview, TopicTemplate, EvaluatorTemplate  # noqa: E402

# --- Example 1: Use a different model as the evaluator ---
# By default the evaluator is Claude. Here we use GPT-4o instead.
result = Interview(
    "claude",
    "openai",
    topics=TopicTemplate.TECHNICAL,
    evaluator="gpt4",
).run(turns=20)
print("=== GPT-4o evaluation ===")
print(result.evaluation)
result.save("technical-gpt4-eval.md")

# --- Example 2: Focus evaluation on technical accuracy ---
result = Interview(
    "claude",
    "openai",
    topics=TopicTemplate.TECHNICAL,
    evaluation_dimensions=EvaluatorTemplate.TECHNICAL_DIMENSIONS,
).run(turns=20)
print("\n=== Technical accuracy evaluation ===")
print(result.evaluation)
result.save("technical-accuracy-eval.md")

# --- Example 3: Custom system prompt — terse, skeptical reviewer ---
result = Interview(
    "openai",
    "claude",
    evaluator_system_prompt=(
        "You are a terse, skeptical reviewer. Assume claims are overblown until "
        "proven with specifics. One paragraph maximum per section. No flattery."
    ),
).run(turns=20)
print("\n=== Skeptical evaluation ===")
print(result.evaluation)
result.save("skeptical-eval.md")

# --- Example 4: Fully custom user prompt ---
# FILENAME: and EVALUATION: markers are optional — the parser falls back gracefully.
result = Interview(
    "openai",
    "claude",
    evaluator_user_prompt=(
        "Read this interview transcript and score the interviewee on three dimensions, "
        "1-10 each, with a one-sentence justification per score:\n\n"
        "- Depth: did answers go beyond surface-level?\n"
        "- Honesty: did the interviewee acknowledge limits?\n"
        "- Clarity: were answers easy to follow?\n\n"
        "Reply with only a markdown table."
    ),
).run(turns=20)
print("\n=== Scorecard evaluation ===")
print(result.evaluation)
result.save("scorecard-eval.md")
