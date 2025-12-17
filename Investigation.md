# LiteLLM Investigation

## What is LiteLLM 

Put simply LiteLLM is a universal API for interfacing with LLMs. This means that provider specific code
is abstracted away from the user. 

## What are the main use cases for LiteLLM

1) Allows users to control:
 - Cost Tracing: User, Project, and Org level Tracing.
 - Budgets: 
    * Control budgets for how much of a particular LLM cost you wish to incur. 
    * Control what times LLMs can be used, (off hours vs on hours)
2) Standadizes Image Gen
2) Standadises Chat Completions 

## LiteLLM Compared to Llamastack

LiteLLM is not a one to one with llamastack. LiteLLM rather provides users with a way to control
llm usage at a variety of levels. 

LiteLLM doesn't have the same builtin like llamastack, like rag, agents, and other items. 

But LiteLLM could interface with llamastack and provide a way for users/developers to swap 
out and change models on the fly and not have to change code. This would give the control 
for the llm useage back to the user. 

Example:
```
# Client SDK → Llama Stack Server → LiteLLM Proxy → 100+ LLM APIs
```
```bash
pip install 'litellm[proxy]'

# Set your provider API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Start the proxy (running on http://0.0.0.0:4000 by default)
litellm --model anthropic/claude-3-5-sonnet-20240620
```

```yaml
name: litellm-distribution
distribution_spec:
  description: "Llama Stack using LiteLLM as the inference backend"
  providers:
    inference: remote::openai  # This tells Llama Stack to use OpenAI's API format
    safety: inline::llama-guard
    vector_io: inline::faiss
    datasetio: inline::localfs
    scoring: inline::basic
    eval: inline::basic
```

```bash
llama stack build --config litellm-build.yaml --image-name llama-stack-litellm
```

```yaml
# ... (standard headers from llama stack run)
providers:
  inference:
    - provider_id: litellm-proxy
      provider_type: remote::openai
      config:
        url: "http://localhost:4000/v1"  # Points to your LiteLLM Proxy
        api_key: "not-needed-for-proxy"  # LiteLLM proxy handles the real key
```

```python
from llama_stack_client import LlamaStackClient

client = LlamaStackClient(base_url="http://localhost:8321")

# Use the Llama Stack API (which is now routing THROUGH LiteLLM)
response = client.inference.chat_completion(
    model_id="anthropic/claude-3-5-sonnet-20240620", 
    messages=[
        {"role": "user", "content": "How does Llama Stack feel about LiteLLM?"}
    ]
)

print(response.completion_message.content)
```

## Why use this integration?

Model Agnostic: Use Llama Stack’s agentic features with non-Llama models (e.g., Claude 3.5 or GPT-4o).

Production Resilience: Enable automatic fallbacks, retries, and load balancing across multiple LLM providers.

Unified Security: Manage API keys, set spend limits, and track usage through a single LiteLLM gateway.

Infrastructure Decoupling: Change your model provider in LiteLLM without needing to rebuild or reconfigure your Llama Stack distribution.

# Agents

1. LiteLLM with an Agent Framework (Recommended)
Most popular agent libraries use LiteLLM under the hood. This gives you the high-level "Agent" features of Llama Stack but with the model flexibility of LiteLLM.

| Framework    | Relationship to LiteLLM                                                   | Best For                                    |
|--------------|--------------------------------------------------------------------------|----------------------------------------------|
| CrewAI       | Uses LiteLLM by default to call models.                                  | Role-based multi-agent teams.                |
| Pydantic AI  | Has a native "A2A" (Agent-to-Agent) gateway through LiteLLM.             | Type-safe, production-heavy agents.          |
| Smolagents   | Uses LiteLLM to let small agents write and run code.                     | Minimalist, code-executing agents.           |
| LangGraph    | Frequently paired with LiteLLM for multi-provider routing.               | Complex, custom-coded agent state machines.  |

# MCP and Tool Calling

1. LiteLLM: The "Pass-Through" Gateway
In LiteLLM, MCP support is handled at the proxy level.

**How it works:**
    You connect an MCP server to LiteLLM. LiteLLM then takes the tools from that server and "injects" them into the API call of whatever model you are using (OpenAI, Claude, etc.).


**Execution:**
    LiteLLM is responsible for the loop. It sees that the model wants to use a tool, it calls the MCP server for you, gets the result, and sends it back to the model.

**Best For:**
    Adding tools to simple Chat applications. If you just want your "Chat with GPT-4" to be able to read your local files via MCP, LiteLLM makes this transparent to your code.

2. Llama Stack: The "Agentic" Orchestrator
In Llama Stack, MCP is treated as a Resource within an agent's ecosystem.

**How it works:**
     You register MCP servers as "Tool Groups" in your Llama Stack distribution. The Llama Stack Agent API then manages these tools.

**Execution:**
    Llama Stack manages the Agent State. Because Llama Stack is designed for complex agents (multi-turn, persistent memory, safety shields), it treats the MCP tool call as one step in a larger "Turn." It handles safety checks (Llama Guard) before and after the MCP tool is even used.

**Best For:**
    Building "Autonomous Agents." If you need an agent that uses an MCP tool to fetch data, thinks about it, uses a second tool to save it, and passes a safety check at every step, Llama Stack is the framework for that.

# Rag and Vector Stores

## Llama Stack: The Managed Pipeline
Llama Stack is an End-to-End Orchestrator. It manages the entire lifecycle of your data internally.

**Internal Workflow:**
    It handles document chunking, embedding, and storage automatically.

**Vector DB**
    Support: Connects directly to databases like FAISS, Chroma, or Milvus.

**Agent Integration:**
    Agents have "Memory" as a native tool; they automatically decide when to search the vector store to answer a question.

**Best For:**
    Building and owning your custom RAG infrastructure from scratch.

## LiteLLM: The Unified Gateway
LiteLLM is a Routing Layer. It connects your app to "Managed RAG" services provided by others.

**Internal Workflow:**
    It acts as a passthrough. It expects your data to already be uploaded to a provider (like OpenAI or AWS Bedrock).

**Provider Support:**
    Maps diverse APIs (OpenAI "File Search," AWS Bedrock Knowledge Bases) to a single OpenAI-compatible format.

**Switchability:**
    Swap your entire RAG backend (e.g., from OpenAI to Gemini) by changing one line of config without touching your application code.

**Best For:**
    Accessing cloud-hosted RAG features across multiple different AI vendors.