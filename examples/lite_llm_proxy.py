# This file is a simple example of how to use LiteLLM to perform a completion.
from ollama import Client

client = Client(
  host='http://localhost:4000', # proxy host url
)

response = client.chat(model='ollama/llama3', messages=[
  {
    'role': 'user',
    'content': 'this is a test request, write a short poem',
  },
])