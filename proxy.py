from ollama import Client

client = Client(
  host='http://localhost:4000',
)

response = client.chat(model='ollama/llama3', messages=[
  {
    'role': 'user',
    'content': 'this is a test request, write a short poem',
  },
])