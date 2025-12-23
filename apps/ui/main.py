import streamlit as st
import requests
import os

st.title("LiteLLM Model Browser")

# Get LiteLLM URL from environment variable, secrets, or default
LITELLM_URL = "http://litellm:4000"
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")

def fetch_models(endpoint):
    try:
        headers = {}
        if LITELLM_API_KEY:
            headers["Authorization"] = f"Bearer {LITELLM_API_KEY}"
        res = requests.get(f"{endpoint}/models", headers=headers)
        res.raise_for_status()
        return res.json().get("data", [])
    except Exception as e:
        st.error(f"Error fetching models: {e}")
        return []

st.sidebar.header("LiteLLM Proxy Settings")
litellm_url = st.sidebar.text_input("LiteLLM URL", value=LITELLM_URL)

if st.button("Fetch Models"):
    models = fetch_models(litellm_url)
    st.write(f"Found {len(models)} models:")
    for model in models:
        st.json(model)
