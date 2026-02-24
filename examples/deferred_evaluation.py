"""Deferred evaluation example — run the conversation now, evaluate later."""

from dotenv import load_dotenv
load_dotenv()

from llm_talk import Interview  # noqa: E402

# Run the interview without triggering the evaluator API call
result = Interview("openai", "claude").run(evaluate=False)

print(f"Interview complete ({result.total_turns} turns). Evaluation not yet run.")

# Save the transcript now if desired — evaluation section will show a placeholder
result.save("output_no_eval.md")

# ... do other work, or decide conditionally whether to evaluate ...

# Trigger evaluation when ready
result.evaluate()
print(result.evaluation)

# Save again with the full evaluation included
result.save("output.md")
print("Saved full report to output.md")
