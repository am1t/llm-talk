# llm-talk

LLM-to-LLM interview framework for evaluating conversational capabilities.

Let LLMs interview each other to reveal strengths, weaknesses, and surprising behaviors that benchmarks miss.

## Quick Start

```python
from llm_talk import Interview

result = Interview("openai", "claude").run()
result.save("output.md")
print(result.evaluation)
```

## Installation

```bash
pip install llm-talk
```

Set your API keys as environment variables:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

### Model Aliases

Use short names or full `provider:model` strings:

| Alias | Resolves to |
|-------|------------|
| `openai` | `openai:gpt-4o-mini` |
| `claude` | `anthropic:claude-sonnet-4-5` |
| `gpt4` | `openai:gpt-4o` |
| `sonnet` | `anthropic:claude-sonnet-4-5` |
| `opus` | `anthropic:claude-opus-4-5` |
| `gemini` | `google:gemini-2.0-flash` |
| `mistral` | `mistral:mistral-large-latest` |

```python
Interview("openai:gpt-4o", "anthropic:claude-opus-4-5").run()
```

### Custom Topics

```python
result = Interview(
    "openai", "claude",
    topics="Test their reasoning and code generation capabilities"
).run(turns=30)
```

### Topic Templates

```python
from llm_talk import Interview, TopicTemplate

result = Interview("openai", "claude", topics=TopicTemplate.TECHNICAL).run()
```

Available templates: `DEFAULT`, `TECHNICAL`, `CREATIVE`, `CULTURAL`.

### Control Turn Count

```python
result = Interview("openai", "claude").run(turns=100)
```

### Custom Evaluator

By default, Claude evaluates the conversation. You can change the evaluator model, dimensions, or prompt:

```python
from llm_talk import Interview, EvaluatorTemplate

# Use a different model as evaluator
result = Interview("claude", "openai", evaluator="gpt4").run()

# Focus evaluation on specific dimensions
result = Interview(
    "claude", "openai",
    evaluation_dimensions=EvaluatorTemplate.TECHNICAL_DIMENSIONS,
).run()

# Override the evaluator system prompt
result = Interview(
    "openai", "claude",
    evaluator_system_prompt="You are a terse, skeptical reviewer. One paragraph per section. No flattery.",
).run()

# Fully custom evaluator prompt
result = Interview(
    "openai", "claude",
    evaluator_user_prompt="Score the interviewee on depth, honesty, and clarity (1-10 each). Reply with a markdown table.",
).run()
```

### Access Results

```python
result = Interview("openai", "claude").run()

print(result.evaluation)        # Claude's evaluation
print(result.total_turns)       # Actual turns completed
print(result.loop_detected)     # Was a loop detected?
print(result.loop_reason)       # Why the loop was detected

result.save("interview.md")     # Save as markdown
data = result.to_dict()         # Export as dict (for JSON)
```

## How It Works

1. Two LLM agents are created — one as interviewer, one as interviewee
2. They have a natural conversation for the specified number of turns
3. Loop detection monitors for repetitive patterns (farewell loops, etc.)
4. Claude evaluates the conversation quality and generates a report
5. Results include the full conversation, evaluation, and metadata

## Examples

See the [examples/](examples/) directory for more usage patterns:

- [basic_interview.py](examples/basic_interview.py) — simplest usage
- [custom_topics.py](examples/custom_topics.py) — focused topic areas
- [custom_evaluator.py](examples/custom_evaluator.py) — evaluator model, dimensions, and prompts
- [batch_experiments.py](examples/batch_experiments.py) — run multiple interviews
- [compare_models.py](examples/compare_models.py) — compare different models

## Development

```bash
git clone https://github.com/am1t/llm-talk.git
cd llm-talk
pip install -e ".[dev]"
pytest
```

To run the example scripts, also install the examples extra:

```bash
pip install -e ".[examples]"
```

## License

MIT
