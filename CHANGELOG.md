# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-02-24

### Fixed

- Unused exception variable in `AIAgent.respond()` caught by ruff (F841)

## [0.2.0] - 2026-02-24

### Added

- `Interview.run(evaluate=False)` to skip the evaluator API call and return immediately after the conversation
- `InterviewResult.evaluate()` to trigger evaluation on demand; idempotent — safe to call multiple times
- `InterviewResult` stores evaluator config privately so `.evaluate()` needs no extra arguments
- `InterviewResult.__str__()` and `generate_markdown()` render a placeholder when evaluation has not been run
- Example script `examples/deferred_evaluation.py` demonstrating the deferred evaluation workflow

### Fixed

- Path traversal vulnerability in `InterviewResult.save()` — relative paths that resolve outside the current directory now raise `ValueError`
- Evaluator exceptions are no longer silently swallowed

## [0.1.0] - 2026-02-21

### Added

- `Interview` class for orchestrating LLM-to-LLM conversations
- `InterviewResult` with `save()` (markdown) and `to_dict()` (JSON-ready) export
- `AIAgent` — unified agent wrapper via [aisuite](https://github.com/andrewyng/aisuite) supporting OpenAI, Anthropic, Google, Mistral, and more
- Built-in conversation loop detection (farewell patterns, repetitive responses, back-and-forth cycles)
- Pluggable evaluator with default and custom dimensions, system/user prompt overrides
- `TopicTemplate` presets: `DEFAULT`, `TECHNICAL`, `CREATIVE`, `CULTURAL`
- `EvaluatorTemplate` presets: `DEFAULT_DIMENSIONS`, `SAFETY_DIMENSIONS`, `TECHNICAL_DIMENSIONS`
- Model alias shortcuts (`openai`, `claude`, `gpt4`, `gemini`, `mistral`, …)
- Progress indicator during interview runs
- Markdown transcript formatter
- Five example scripts covering basic usage, custom topics, custom evaluators, batch experiments, and model comparison
- Full type annotations and `py.typed` marker
- Test suite covering agents, core orchestration, evaluators, detectors, formatters, and model resolution

[0.2.1]: https://github.com/am1t/llm-talk/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/am1t/llm-talk/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/am1t/llm-talk/releases/tag/v0.1.0
