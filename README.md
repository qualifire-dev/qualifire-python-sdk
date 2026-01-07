# Qualifire Python SDK

<div align="center">

[![build](https://github.com/qualifire-dev/qualifire-python-sdk/actions/workflows/build.yml/badge.svg)](https://github.com/qualifire-dev/qualifire-python-sdk/actions/workflows/build.yml)
[![Python Version](https://img.shields.io/pypi/pyversions/qualifire.svg)](https://pypi.org/project/qualifire/)
[![License](https://img.shields.io/github/license/qualifire-dev/qualifire)](https://github.com/qualifire-dev/qualifire/blob/main/LICENSE)
![Coverage Report](assets/images/coverage.svg)

**Evaluate your LLM outputs for quality, safety, and reliability**

</div>

---

## Overview

The Qualifire Python SDK provides a simple interface to evaluate LLM outputs against a comprehensive suite of quality and safety checks. Detect hallucinations, ensure grounding, identify PII, block harmful content, and validate that your AI follows instructions—all through a single API.

## Installation

```bash
pip install qualifire
```

Or with Poetry:

```bash
poetry add qualifire
```

## Quick Start

```python
from qualifire.client import Client

# Initialize the client
client = Client(api_key="your_api_key")

# Evaluate an LLM response
result = client.evaluate(
    input="What is the capital of France?",
    output="The capital of France is Paris.",
    hallucinations_check=True,
    grounding_check=True,
)

print(f"Score: {result.score}")
print(f"Status: {result.status}")
```

## Available Checks

| Check                          | Description                                                                            |
| ------------------------------ | -------------------------------------------------------------------------------------- |
| `hallucinations_check`         | Detect factual inaccuracies or hallucinations                                          |
| `grounding_check`              | Verify output is grounded in the provided context                                      |
| `pii_check`                    | Detect personally identifiable information                                             |
| `prompt_injections`            | Identify prompt injection attempts                                                     |
| `content_moderation_check`     | Check for harmful content (harassment, hate speech, dangerous content, sexual content) |
| `tool_use_quality_check` | Evaluate quality of tool/function calls                                                |
| `syntax_checks`                | Validate output syntax (JSON, SQL, etc.)                                               |
| `assertions`                   | Custom assertions to validate against the output                                       |

## Usage Examples

### Basic Evaluation

```python
from qualifire.client import Client

client = Client(api_key="your_api_key")

result = client.evaluate(
    input="Summarize this document about climate change.",
    output="Climate change is primarily caused by human activities...",
    hallucinations_check=True,
    grounding_check=True,
)
```

### Messages-based Evaluation

```python
from qualifire.client import Client
from qualifire.types import LLMMessage

client = Client(api_key="your_api_key")

result = client.evaluate(
    messages=[
        LLMMessage(role="system", content="You are a helpful assistant."),
        LLMMessage(role="user", content="What is the capital of France?"),
        LLMMessage(role="assistant", content="The capital of France is Paris."),
    ],
    hallucinations_check=True,
    grounding_check=True,
)
```

### Content Moderation

```python
result = client.evaluate(
    input="Write a story about friendship.",
    output="Once upon a time...",
    content_moderation_check=True,
    pii_check=True,
)
```

### Syntax Validation

```python
from qualifire.types import SyntaxCheckArgs

result = client.evaluate(
    input="Return the user data as JSON.",
    output='{"name": "John", "age": 30}',
    syntax_checks={
        "json": SyntaxCheckArgs(args="strict")
    },
)
```

### Multi-Turn Conversations

```python
from qualifire.types import LLMMessage

result = client.evaluate(
    messages=[
        LLMMessage(role="user", content="What is 2 + 2?"),
        LLMMessage(role="assistant", content="2 + 2 equals 4."),
        LLMMessage(role="user", content="And if you add 3 more?"),
        LLMMessage(role="assistant", content="4 + 3 equals 7."),
    ],
    hallucinations_check=True,
    grounding_multi_turn_mode=True,
)
```

### Tool Selection Quality

```python
from qualifire.types import LLMMessage, LLMToolCall, LLMToolDefinition

result = client.evaluate(
    messages=[
        LLMMessage(
            role="user",
            content="What's the weather in New York tomorrow?",
        ),
        LLMMessage(
            role="assistant",
            content="Let me check that for you.",
            tool_calls=[
                LLMToolCall(
                    id="call_123",
                    name="get_weather",
                    arguments={"location": "New York", "date": "tomorrow"},
                )
            ],
        ),
    ],
    available_tools=[
        LLMToolDefinition(
            name="get_weather",
            description="Get weather forecast for a location",
            parameters={
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "date": {"type": "string"},
                },
                "required": ["location"],
            },
        ),
    ],
    tool_use_quality_check=True,
)
```

### Custom Assertions

```python
result = client.evaluate(
    input="List three fruits.",
    output="1. Apple\n2. Banana\n3. Orange",
    assertions=[
        "The output must contain exactly three items",
        "Each item must be a fruit",
        "Items must be numbered",
    ],
)
```

### Invoke Pre-configured Evaluations

```python
# Run an evaluation configured in the Qualifire dashboard
result = client.invoke_evaluation(
    evaluation_id="eval_abc123",
    input="User query here",
    output="LLM response here",
)
```

## Configuration

### Environment Variables

| Variable             | Description                    |
| -------------------- | ------------------------------ |
| `QUALIFIRE_API_KEY`  | Your Qualifire API key         |
| `QUALIFIRE_BASE_URL` | Custom API base URL (optional) |

### Client Options

```python
client = Client(
    api_key="your_api_key",      # API key (or use env var)
    base_url="https://...",       # Custom base URL
    debug=True,                   # Enable debug mode
    verify=True,                  # SSL verification
)
```

## Model Modes

Control the speed/quality trade-off for different checks:

```python
from qualifire.types import ModelMode

result = client.evaluate(
    input="...",
    output="...",
    hallucinations_check=True,
    hallucinations_mode=ModelMode.QUALITY,  # SPEED | BALANCED | QUALITY
    grounding_check=True,
    grounding_mode=ModelMode.SPEED,
)
```

## Response Format

```python
result = client.evaluate(...)

# Overall score (0-100)
print(result.score)

# Status of the evaluation
print(result.status)

# Detailed results per check
for item in result.evaluationResults:
    print(f"Check type: {item.type}")
    for r in item.results:
        print(f"  - {r.name}: {r.label} (score: {r.score})")
        print(f"    Reason: {r.reason}")
        print(f"    Flagged: {r.flagged}")
```

## Requirements

- Python 3.8+

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Links

- [Documentation](https://docs.qualifire.ai)
- [Qualifire Dashboard](https://app.qualifire.ai)
- [GitHub Repository](https://github.com/qualifire-dev/qualifire-python-sdk)
