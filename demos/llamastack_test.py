from llama_stack_client import LlamaStackClient

client = LlamaStackClient(
    base_url="https://litellm-hacohen-llmlite.apps.ai-dev02.kni.syseng.devcluster.openshift.com",  # Your LiteLLM URL
    api_key= "master-key"
)

# 1. List available models (Proves LiteLLM is forwarding the model list)
models = client.models.list()
print("Available Models:", models)
print("Total Available Models:", len(models))


# 2. Run an Inference Call
response = client.chat.completions.create(
    model="llama3", #"llama-fp8", # LiteLLM maps this to your local Llama 3
    messages=[
        {"role": "user", "content": "Hello! Are you compatible with Llama Stack?"}
    ]
)

print("\nResponse:", response.choices[0].message.content)