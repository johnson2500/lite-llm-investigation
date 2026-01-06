# LiteLLM Failover Demo

Demonstrates LiteLLM's automatic failover routing feature. When the primary model becomes unavailable, LiteLLM automatically routes requests to a fallback model.

## Prerequisites

- Python 3.10+
- Access to a running LiteLLM proxy server with failover configured
- Required packages: `openai`

Install dependencies:
```bash
pip install openai
```

## LiteLLM Configuration

Add `router_settings` with fallback configuration to your LiteLLM config (`values.yaml`):

```yaml
litellm:
  config:
    model_list:
      - model_name: llama3
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama:11434
      
      - model_name: llama-fp8
        litellm_params:
          model: openai/llama-fp8
          api_base: http://llama-fp8-predictor:8080/v1

    # Fallback routing configuration
    router_settings:
      fallbacks:
        - "llama-fp8": ["llama3"]
      num_retries: 0           # Failover immediately
      timeout: 30              # 30 second timeout
      allowed_fails: 1
      cooldown_time: 10        # Cooldown failed model for 10 seconds
```

## What it does

1. Sends continuous requests to the primary model (`llama-fp8`)
2. Detects when the primary model becomes unavailable
3. Shows automatic failover to the fallback model (`llama3`)
4. Detects when the primary model recovers and switches back

## Run

```bash
python failover_test.py
```

To test failover:
1. Start the script
2. In another terminal, scale down the primary model:
   ```bash
   oc scale deployment llama-fp8-predictor --replicas=0
   ```
3. Watch requests failover to llama3
4. Scale back up to see recovery:
   ```bash
   oc scale deployment llama-fp8-predictor --replicas=1
   ```

## Example Output

### Normal Operation (Primary Model)
```
======================================================================
LiteLLM Failover Demo
======================================================================
  Primary Model: llama-fp8
  Fallback Model: llama3 (configured in router_settings)
  Request Interval: 3s
======================================================================

[*] Sending requests to primary model...
[*] To test failover: restart the llama-fp8 service in another terminal
[*] Press Ctrl+C to stop

----------------------------------------------------------------------
[13:40:47] Request #1: ✓ PRIMARY
           Model: llama-fp8
           Response: Hi.

[13:40:51] Request #2: ✓ PRIMARY
           Model: llama-fp8
           Response: Hi

[13:40:54] Request #3: ✓ PRIMARY
           Model: llama-fp8
           Response: Hi
```

### Failover to Fallback Model
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[!] FAILOVER DETECTED: llama-fp8 → ollama/llama3
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

[13:40:57] Request #4: ✓ FALLBACK
           Model: ollama/llama3
           Response: Hello!

[13:41:01] Request #5: ✓ FALLBACK
           Model: ollama/llama3
           Response: Hello!

[13:41:10] Request #6: ✓ FALLBACK
           Model: ollama/llama3
           Response: Hello!
```

### Recovery to Primary Model
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
[!] FAILOVER DETECTED: ollama/llama3 → llama-fp8
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

[13:45:55] Request #52: ✓ PRIMARY
           Model: llama-fp8
           Response: Hi.

[13:45:58] Request #53: ✓ PRIMARY
           Model: llama-fp8
           Response: Hi

[13:46:01] Request #54: ✓ PRIMARY
           Model: llama-fp8
           Response: Hi
```

### Final Summary
```
======================================================================
Demo Summary
======================================================================
  • Total requests: 59
  • Successful: 59
  • Failed: 0
  • Failover: ✓ Detected and handled
======================================================================
```

## Configuration Options

| Parameter | Description |
|-----------|-------------|
| `fallbacks` | Map of model → fallback models list |
| `num_retries` | Number of retries before falling back (0 = immediate) |
| `timeout` | Request timeout in seconds |
| `allowed_fails` | Failures before putting model in cooldown |
| `cooldown_time` | Seconds to wait before retrying a failed model |

## Key Observations

1. **Fast Failover**: With `num_retries: 0`, failover happens immediately after a failure
2. **Automatic Recovery**: After `cooldown_time` expires, LiteLLM tries the primary model again
3. **Transparent to Client**: The client code doesn't need to handle failover logic - LiteLLM manages it automatically
4. **Model Tracking**: Response includes which model actually served the request

## LiteLLM APIs Used

| Endpoint | Description |
|----------|-------------|
| `POST /v1/chat/completions` | OpenAI-compatible completions endpoint |

