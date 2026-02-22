"""AI agent for conversations using aisuite."""

import logging
from dataclasses import dataclass, field
import aisuite

logger = logging.getLogger(__name__)


@dataclass
class AIAgent:
    """Represents an AI agent in a conversation.

    Uses aisuite for unified access to any LLM provider.
    """

    name: str
    model: str
    system_prompt: str
    client: aisuite.Client = field(default=None, repr=False)
    messages: list[dict[str, str]] = field(default_factory=list, repr=False)

    def __post_init__(self):
        """Initialize client and seed messages with system prompt."""
        if self.client is None:
            self.client = aisuite.Client()
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def add_user_message(self, content: str):
        """Add a user message to history."""
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """Add an assistant message to history."""
        self.messages.append({"role": "assistant", "content": content})

    def respond(self) -> str:
        """Get response from this agent via aisuite.

        Returns the model's reply, or an error string if the API call fails.
        The error string is returned (not raised) so callers can preserve
        conversation progress accumulated before the failure.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as exc:
            logger.exception("API call failed for agent %r (model %r)", self.name, self.model)
            return f"[{self.name} could not generate a response]"
