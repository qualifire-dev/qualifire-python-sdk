# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Qualifire Python SDK - A library for evaluating LLM outputs for quality, safety, and reliability. Detects hallucinations, ensures grounding, identifies PII, blocks harmful content, and validates instruction-following through a single API.

## Development Commands

```bash
# Install dependencies and set up environment
make install
make pre-commit-install

# Run tests with coverage
make test

# Run a single test file
uv run pytest tests/test_types.py

# Run a specific test
uv run pytest tests/test_types.py::TestEvaluationRequest::test_validate_messages_input_output -v

# Format code (isort, black, pyupgrade)
make codestyle

# Check code style without modifying
make check-codestyle

# Run type checking
make mypy

# Run all checks (tests, codestyle, mypy, safety)
make lint

# Check for security issues
make check-safety
```

## Architecture

The SDK has a minimal structure centered on the `Client` class:

- **`qualifire/client.py`**: Main `Client` class with two public methods:
  - `evaluate()` - Run ad-hoc evaluations with various checks (hallucinations, grounding, PII, content moderation, etc.)
  - `invoke_evaluation()` - Run pre-configured evaluations from the Qualifire dashboard

- **`qualifire/types.py`**: All data classes and enums:
  - `EvaluationRequest`/`EvaluationResponse` - API request/response structures
  - `LLMMessage`, `LLMToolCall`, `LLMToolDefinition` - Message and tool types for conversation-based evaluation
  - `ModelMode` (SPEED/BALANCED/QUALITY) - Quality vs speed trade-off for checks
  - `SyntaxCheckArgs` - Configuration for syntax validation

- **`qualifire/utils.py`**: Helper functions for API key and base URL resolution from environment variables

## Key Patterns

- API key can be passed directly or via `QUALIFIRE_API_KEY` environment variable
- Base URL defaults to `https://proxy.qualifire.ai/` but can be overridden via `QUALIFIRE_BASE_URL`
- The `EvaluationRequest` dataclass validates inputs in `__post_init__` (e.g., tool_selection_quality_check requires both messages and available_tools)
- Legacy content moderation checks (dangerous_content_check, harassment_check, etc.) are deprecated in favor of unified `content_moderation_check`

## Testing

Tests are in `tests/` and use pytest with parametrized test cases. Run `make test` for the full suite with coverage report.
