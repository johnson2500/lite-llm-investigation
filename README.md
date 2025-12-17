# lite_llm_proxy.py
Demonstrates the proxied version of liteLLM to track projects and users.

## Starting the server

`litellm --model huggingface/bigcode/starcoder`

```
import openai

client = openai.OpenAI(api_key="anything",base_url="http://0.0.0.0:4000") # set proxy to base_url
# request sent to model set on litellm proxy, `litellm --model`

response = client.chat.completions.create(model="ollama/llama3", messages = [
    {
        "role": "user",
        "content": "this is a test request, write a short poem"
    }
])

print(response)
```

# main.py 

Focuses on the base functionlity of lite LLM.