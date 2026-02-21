"""Basic interview example — the simplest way to use llm-talk."""

from dotenv import load_dotenv
load_dotenv()

from llm_talk import Interview

# Run an interview between OpenAI and Claude
result = Interview("openai", "claude").run()

# Print the evaluation
print(result.evaluation)

# Save to markdown
result.save("output.md")
print(f"Saved to output.md ({result.total_turns} turns)")
