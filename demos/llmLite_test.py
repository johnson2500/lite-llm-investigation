import litellm
import requests


if __name__ == "__main__":
    url = "https://litellm-hacohen-llmlite.apps.ai-dev02.kni.syseng.devcluster.openshift.com/models"
    headers = {"Authorization": "Bearer master-key"}

    response = requests.get(url, headers=headers)
    models = response.json()

    print("Available models:")
    for model in models["data"]:
        print(f"  - {model['id']}")


    response = litellm.completion(
        model="openai/llama-fp8",
        messages=[
            {"role": "user", "content": "What is the capital of France? Answer in one sentence."}
        ],
        api_base="https://litellm-hacohen-llmlite.apps.ai-dev02.kni.syseng.devcluster.openshift.com",
        api_key="master-key",
    )

    print("Response:", response.choices[0].message.content)
