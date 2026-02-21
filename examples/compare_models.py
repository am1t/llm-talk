"""Compare models — same interviewer, different interviewees."""

from dotenv import load_dotenv
load_dotenv()

from llm_talk import Interview, TopicTemplate  # noqa: E402

interviewees = ["openai", "claude", "gemini"]

for model in interviewees:
    print(f"\n--- Interviewing {model} ---")
    result = Interview("claude", model, topics=TopicTemplate.CREATIVE).run(turns=25)
    result.save(f"creative-{model}.md")
    print(f"  {result.total_turns} turns completed")
    print(f"  Loop detected: {result.loop_detected}")
    print()
