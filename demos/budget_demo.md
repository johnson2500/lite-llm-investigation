# LiteLLM Budget Management Demo

Demonstrates LiteLLM's budget management feature for controlling API spend.

## Prerequisites

- Python 3.10+
- Access to a running LiteLLM proxy server
- Required packages: `litellm`, `requests`

Install dependencies:
```bash
pip install litellm requests
```

Or with uv:
```bash
uv add litellm requests
```

## What it does

1. Creates a virtual API key with a small budget limit ($0.001)
2. Sends completion requests until the budget is exhausted
3. Shows how LiteLLM rejects requests once the budget is exceeded
4. Cleans up by deleting the temporary key

## Run

```bash
python budget_test.py
```

## Expected output

```
============================================================
LiteLLM Budget Management Demo
============================================================

[Step 1] Creating virtual key with $0.001 budget...
  ✓ Created key: sk-abc123...
  ✓ Max budget: $0.001

[Step 2] Sending completion requests until budget is exhausted...
------------------------------------------------------------

  Request #1:
    Prompt: Say 'hello' in one word.
    Response: Hi
    Tokens: 15 in / 2 out
    Request cost: $0.000190
    Cumulative spend: $0.000190 / $0.001

  ...

  ✗ REQUEST REJECTED - Budget Exceeded!
    Error: Budget has been exceeded! Current cost: 0.00143, Max budget: 0.001

============================================================
[Step 3] Budget Demo Summary
============================================================
  • Total requests made: 3 (successful)
  • Requests rejected: 1 (budget exceeded)
  • Max budget: $0.001
  • Final spend (from LiteLLM): $0.001430

[Step 4] Cleaning up temporary key...
  ✓ Key deleted successfully
```

## Configuration

Edit these variables in `budget_test.py` to match your environment:

| Variable | Description |
|----------|-------------|
| `BASE_URL` | Your LiteLLM proxy URL |
| `MASTER_KEY` | Admin master key for key management |
| `MODEL` | Model to use for completions |
| `MAX_BUDGET` | Budget limit in USD (default: $0.001) |
| `INPUT_COST_PER_TOKEN` | Cost per input token (must match LiteLLM config) |
| `OUTPUT_COST_PER_TOKEN` | Cost per output token (must match LiteLLM config) |

## Important: Custom Pricing for Self-Hosted Models

For self-hosted models (vLLM, Ollama, etc.), you must configure custom pricing in your LiteLLM `values.yaml`:

```yaml
- model_name: llama-fp8
  litellm_params:
    model: openai/llama-fp8
    api_base: http://your-model-endpoint/v1
    input_cost_per_token: 0.0001   # $0.10 per 1K tokens
    output_cost_per_token: 0.0002  # $0.20 per 1K tokens
```

Without custom pricing, LiteLLM cannot track spend for self-hosted models and budget limits won't work.

## LiteLLM APIs Used

| Endpoint | Description |
|----------|-------------|
| `POST /key/generate` | Create virtual keys with budget limits |
| `GET /key/info` | Get key information and spend |
| `POST /key/delete` | Delete virtual keys |
| `POST /chat/completions` | Make completion requests |

