"""Batch experiments — run multiple interviews and compare results."""

from dotenv import load_dotenv
load_dotenv()

from llm_talk import Interview, TopicTemplate

# Define model pairs to compare
pairs = [
    ("openai", "claude"),
    ("claude", "openai"),
    ("gpt4", "sonnet"),
]

results = []
for interviewer, interviewee in pairs:
    print(f"\n--- {interviewer} interviews {interviewee} ---")
    result = Interview(interviewer, interviewee, topics=TopicTemplate.TECHNICAL).run(turns=20)
    results.append(result)
    result.save()
    print(f"  Turns: {result.total_turns}, Loop: {result.loop_detected}")

# Summary
print("\n=== Summary ===")
for (interviewer, interviewee), result in zip(pairs, results):
    print(f"{interviewer} -> {interviewee}: {result.total_turns} turns, loop={result.loop_detected}")
