# LiteLLM Streamlit UI

A simple Streamlit-based web UI for browsing models exposed by the LiteLLM proxy.

> **Deployment:** This UI is deployed via the Helm chart in `../../litellm/helm/`. See [../../litellm/DEPLOYMENT.md](../../litellm/DEPLOYMENT.md) for instructions.

## Project Structure

```
.
├── main.py              # Streamlit application
├── requirements.txt     # Python dependencies
├── Containerfile        # Container image definition
├── config.toml          # Streamlit configuration
└── README.md            # This file
```

## Building the Container Image

### OpenShift

```bash
oc new-build --name litellm-ui --binary --strategy docker -n litellm
oc start-build litellm-ui --from-dir=. --follow -n litellm
```

### Podman/Docker

```bash
podman build -t litellm-ui:latest -f Containerfile .
podman push <your-registry>/litellm-ui:latest
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set LiteLLM URL
export LITELLM_URL=http://localhost:4000

# Run the app
streamlit run main.py
```

Access at `http://localhost:8501`

### Testing with Deployed LiteLLM

```bash
# Port-forward to the deployed service
kubectl port-forward -n litellm svc/litellm 4000:4000

# Run locally
export LITELLM_URL=http://localhost:4000
streamlit run main.py
```

## Modifying the UI

1. Edit `main.py`
2. Test locally with `streamlit run main.py`
3. Rebuild the image (see above)
4. Restart the deployment:
   ```bash
   oc rollout restart deployment/litellm-ui -n litellm
   ```
