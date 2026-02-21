"""Custom topics example — focus the interview on specific areas."""

from dotenv import load_dotenv
load_dotenv()

from llm_talk import Interview  # noqa: E402

# Define your own topics
result = Interview(
    "openai",
    "claude",
    topics=[
        "Indian language capabilities (Hindi, Tamil, Bengali — test translations)",
        "Understanding of Indian culture, history, and current events",
        "Code-switching between English and Indian languages",
    ],
).run(turns=30)

print(result.evaluation)
result.save("indian-languages.md")
