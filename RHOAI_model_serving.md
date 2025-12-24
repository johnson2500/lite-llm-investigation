# Serving Models with OpenShift AI and LiteLLM

This guide explains how to deploy a model using OpenShift AI (RHOAI) and integrate it with LiteLLM for unified API access.

## Prerequisites

- OpenShift AI (RHOAI) installed on your cluster
- GPU nodes available (for optimal performance)
- LiteLLM proxy deployed (see `litellm/DEPLOYMENT.md`)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenShift Namespace                          │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   LiteLLM    │◄───│    Client    │    │   OpenShift AI   │  │
│  │   Proxy      │    │   Request    │    │   vLLM Server    │  │
│  │  Port 4000   │    └──────────────┘    │   Port 8080      │  │
│  └──────┬───────┘                        └────────▲─────────┘  │
│         │                                         │             │
│         └─────────────────────────────────────────┘             │
│                    model: llama-fp8                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step 1: Deploy Model via OpenShift AI Dashboard

### 1.1 Access the Dashboard

1. Open the OpenShift Console
2. Click on the **Application Launcher** (grid icon) in the top navigation
3. Select **Red Hat OpenShift AI**

### 1.2 Create or Select a Data Science Project

1. Go to **Data Science Projects**
2. Select an existing project or click **Create data science project**

### 1.3 Deploy the Model

1. Inside your project, scroll to the **Models** section
2. Click **Deploy model** under Single-model serving platform
3. Configure the model:

| Field | Value | Notes |
|-------|-------|-------|
| **Model name** | `llama-fp8` | This becomes the model ID in vLLM |
| **Serving runtime** | `vLLM ServingRuntime for KServe` | Recommended for FP8 models |
| **Model framework** | `vLLM` | |
| **Model server size** | Medium or Large | Needs ~8GB memory minimum |
| **Accelerator** | Select your GPU type | Required for FP8 models |
| **Model location** | URI - v1 | Simplest for HuggingFace models |
| **URI** | `hf://RedHatAI/Llama-3.2-1B-Instruct-FP8` | HuggingFace model path |

4. Click **Deploy**

### 1.4 Wait for Model to Load

- The model will show "Loading" status while downloading from HuggingFace
- Wait until status changes to **Loaded** (may take 5-10 minutes)

---

## Step 2: Get the Model Endpoint

### 2.1 Find the Service URL

```bash
oc get inferenceservice -n <YOUR_NAMESPACE>
```

Example output:
```
NAME        URL                                                                   READY
llama-fp8   http://llama-fp8-predictor.<NAMESPACE>.svc.cluster.local             True
```

### 2.2 Find the Correct Port

```bash
oc get pods -n <YOUR_NAMESPACE> -l serving.kserve.io/inferenceservice=llama-fp8 -o yaml | grep -A3 "containerPort"
```

Typical output shows port **8080**.

### 2.3 Verify the Model Name in vLLM

```bash
oc exec deployment/litellm -n <YOUR_NAMESPACE> -- python3 -c "
import urllib.request
import json
r = urllib.request.urlopen('http://llama-fp8-predictor.<NAMESPACE>.svc.cluster.local:<PORT>/v1/models', timeout=5)
data = json.loads(r.read().decode())
print('Available models in vLLM:')
for m in data.get('data', []):
    print(f'  - {m[\"id\"]}')"
```

Note the exact model ID (e.g., `llama-fp8`) - you'll need this for the LiteLLM config.

---

## Step 3: Add Model to LiteLLM Configuration

### 3.1 Update values.yaml

Edit `litellm/helm/values.yaml` and add the new model to the `model_list`:

```yaml
litellm:
  config:
    model_list:
      # Existing models...
      - model_name: llama3
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama:11434
      
      # New RHOAI model
      - model_name: llama-fp8
        litellm_params:
          model: openai/llama-fp8          # Must match vLLM model ID
          api_base: http://llama-fp8-predictor.<NAMESPACE>.svc.cluster.local:<PORT>/v1
          api_key: "none"                  # Required - tells LiteLLM no auth needed
```

### 3.2 Key Configuration Fields

| Field | Description | Example |
|-------|-------------|---------|
| `model_name` | Name exposed to API clients | `llama-fp8` |
| `model` | `openai/<vllm-model-id>` - uses OpenAI protocol | `openai/llama-fp8` |
| `api_base` | Internal cluster URL with port and `/v1` | `http://...:<PORT>/v1` |
| `api_key` | Set to `"none"` for internal endpoints | `"none"` |

### 3.3 Apply the Configuration

```bash
cd litellm
helm upgrade litellm ./helm -n <YOUR_NAMESPACE>
```

---

## Step 4: Test the Model

### 4.1 List Available Models

```bash
curl "https://<LITELLM_ROUTE>/models" \
  -H "Authorization: Bearer master-key"
```

Expected output:
```json
{"data":[{"id":"llama3","object":"model"},{"id":"llama-fp8","object":"model"}]}
```

### 4.2 Test Chat Completion

```bash
curl "https://<LITELLM_ROUTE>/chat/completions" \
  -H "Authorization: Bearer master-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-fp8",
    "messages": [{"role": "user", "content": "Hello, how are you?"}]
  }'
```

### 4.3 Test with Python (requests)

```python
import requests

url = "https://<LITELLM_ROUTE>/models"
headers = {"Authorization": "Bearer master-key"}

# List models
response = requests.get(url, headers=headers)
print("Available models:")
for model in response.json()["data"]:
    print(f"  - {model['id']}")

# Chat completion
url = "https://<LITELLM_ROUTE>/chat/completions"
response = requests.post(url, 
    headers={"Authorization": "Bearer master-key", "Content-Type": "application/json"},
    json={"model": "llama-fp8", "messages": [{"role": "user", "content": "Hello!"}]}
)
print("\nResponse:", response.json()["choices"][0]["message"]["content"])
```

### 4.4 Test with Python (LiteLLM SDK)

```python
import litellm

response = litellm.completion(
    model="openai/llama-fp8",
    messages=[
        {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
    ],
    api_base="https://<LITELLM_ROUTE>",
    api_key="master-key",
)

print("Response:", response.choices[0].message.content)
```

---

## Troubleshooting

### Connection Error

If you get a connection error, verify:

1. **Correct port** - vLLM typically uses port 8080
2. **Service exists** - `oc get svc -n <NAMESPACE> | grep llama`
3. **Pod is running** - `oc get pods -n <NAMESPACE> | grep llama`

### Model Not Found (404)

The model name in `values.yaml` must match exactly what vLLM reports:

```bash
# Check what vLLM calls the model
oc exec deployment/litellm -n <NAMESPACE> -- python3 -c "
import urllib.request, json
r = urllib.request.urlopen('http://llama-fp8-predictor.<NAMESPACE>.svc.cluster.local:<PORT>/v1/models')
print(json.loads(r.read()))"
```

### Authentication Error

Add `api_key: "none"` to the model config - this tells LiteLLM the backend doesn't require authentication.

---

## Example: Full values.yaml Model Configuration

```yaml
litellm:
  debug: true
  masterKey: "master-key"
  apiKey: "sk-1234567890"
  config:
    model_list:
      # Local Ollama model
      - model_name: llama3
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama:11434
      
      # OpenShift AI vLLM model
      - model_name: llama-fp8
        litellm_params:
          model: openai/llama-fp8
          api_base: http://llama-fp8-predictor.hacohen-llmlite.svc.cluster.local:8080/v1
          api_key: "none"
      
      # Another RHOAI model example
      - model_name: granite-code
        litellm_params:
          model: openai/granite-code
          api_base: http://granite-code-predictor.hacohen-llmlite.svc.cluster.local:8080/v1
          api_key: "none"
```

---

## Reference Links

- [HuggingFace Model: RedHatAI/Llama-3.2-1B-Instruct-FP8](https://huggingface.co/RedHatAI/Llama-3.2-1B-Instruct-FP8)
- [LiteLLM Documentation](https://docs.litellm.ai/)
- [OpenShift AI Documentation](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed)

