"""llm-talk — LLM-to-LLM interview framework."""

from .core import Interview, InterviewResult
from .templates import TopicTemplate, EvaluatorTemplate

__all__ = ["Interview", "InterviewResult", "TopicTemplate", "EvaluatorTemplate"]
