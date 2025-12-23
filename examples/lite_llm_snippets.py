# This file is a simple example of how to use LiteLLM to perform a completion.
from litellm import completion
import litellm

MODEL_NAME = "ollama/llama3"

def simple_completion(prompt):
    response = completion(
        model=MODEL_NAME,
        messages = [{ "content": prompt,"role": "user"}],
        api_base="http://localhost:11434",
        stream=True,
    )
    for chunk in response:
        print(chunk.choices[0].delta.content, end="", flush=True)

# This function is a simple example of how to use LiteLLM to perform a completion and track the cost.
def track_cost(prompt):
    def track_cost_callback(
        kwargs,                 # kwargs to completion
        completion_response,    # response from completion
        start_time, end_time    # start/end timestamps
    ):
        try:
            response_cost = kwargs.get("response_cost", 0)
            print(f"streaming response_cost: {response_cost}")
        except:
            pass
    # set callback
    litellm.success_callback = [track_cost_callback] # set custom callback function

    # litellm.completion() call
    response = completion(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        stream=True
    )

    for chunk in response:
        print(chunk.choices[0].delta.content, end="", flush=True)

track_cost("Hello, how are you?")
simple_completion("Hello, how are you?")
