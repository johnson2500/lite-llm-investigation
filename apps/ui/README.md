# LiteLLM Streamlit UI

A simple Streamlit-based web UI for browsing and interacting with models exposed by the LiteLLM proxy.

> **Note:** The Helm chart for this UI is now integrated into the main LiteLLM Helm chart at `../../litellm/helm/`. Deploy both services together with a single `helm install` command.

## Features

- 🔍 Browse available models from LiteLLM proxy
- 🔌 Configurable LiteLLM endpoint
- 🚀 Easy deployment to Kubernetes/OpenShift
- 📦 Containerized application
- 🎯 Integrated deployment with LiteLLM

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set LiteLLM URL (optional, defaults to http://localhost:4000)
export LITELLM_URL=http://localhost:4000

# Run the app
streamlit run main.py
```

Access the UI at `http://localhost:8501`

### Deploy to OpenShift/Kubernetes

The UI is now deployed as part of the main LiteLLM Helm chart:

```bash
# Build the UI image
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/apps/ui
oc new-build --name litellm-ui --binary --strategy docker -n litellm
oc start-build litellm-ui --from-dir=. --follow -n litellm

# Deploy both LiteLLM and UI together
cd ../../litellm/helm
helm install litellm . \
  --namespace litellm \
  --create-namespace \
  --set ui.enabled=true \
  --set ui.image.repository=image-registry.openshift-image-registry.svc:5000/litellm/litellm-ui \
  --set ui.image.tag=latest
```

Or use the automated deployment script:

```bash
cd ../../litellm
./deploy-all.sh
```

See [../../litellm/DEPLOYMENT.md](../../litellm/DEPLOYMENT.md) for detailed deployment instructions.

## Project Structure

```
.
├── main.py              # Streamlit application
├── requirements.txt     # Python dependencies
├── Containerfile        # Container image definition
├── config.toml         # Streamlit configuration
├── README.md           # This file
├── DEPLOYMENT.md       # Deployment guide (redirects to main chart)
└── .streamlit/
    └── secrets.toml    # Streamlit secrets (for local dev)

Note: Helm chart is located at ../../litellm/helm/ (unified deployment)
```

## Configuration

The UI can be configured through:

1. **Environment Variable** (highest priority):
   ```bash
   export LITELLM_URL=http://litellm:4000
   ```

2. **Streamlit Secrets** (local development):
   Edit `.streamlit/secrets.toml`:
   ```toml
   litellm_url = "http://localhost:4000"
   ```

3. **Helm Values** (Kubernetes deployment):
   Edit `../../litellm/helm/values.yaml`:
   ```yaml
   ui:
     enabled: true
     # UI automatically connects to LiteLLM service
   ```

## Building the Container Image

### With Podman/Docker

```bash
podman build -t litellm-ui:latest -f Containerfile .
```

### With OpenShift

```bash
oc new-build --name litellm-ui --binary --strategy docker -n litellm
oc start-build litellm-ui --from-dir=. --follow -n litellm
```

## Deployment

### Prerequisites

1. LiteLLM proxy must be deployed first
2. Container image must be built and available

### Deploy with Helm

```bash
cd ../../litellm/helm

# Deploy both LiteLLM and UI
helm install litellm . \
  --namespace litellm \
  --create-namespace \
  --set ui.enabled=true \
  --set ui.image.repository=image-registry.openshift-image-registry.svc:5000/litellm/litellm-ui \
  --set ui.image.tag=latest

# Get the route URLs
oc get route -n litellm
```

See [../../litellm/helm/README.md](../../litellm/helm/README.md) for more configuration options.

## Usage

1. Open the UI in your browser
2. The default LiteLLM URL will be pre-populated
3. Click "Fetch Models" to retrieve available models
4. Browse the model information

## Development

### Adding New Features

The main application is in `main.py`. To add new features:

1. Edit `main.py`
2. Test locally with `streamlit run main.py`
3. Rebuild the container image
4. Redeploy to Kubernetes

### Testing Locally with Remote LiteLLM

```bash
# Port-forward to deployed LiteLLM
kubectl port-forward -n litellm svc/litellm 4000:4000

# Run UI locally
export LITELLM_URL=http://localhost:4000
streamlit run main.py
```

## Troubleshooting

### Cannot connect to LiteLLM

1. Check LiteLLM is running:
   ```bash
   kubectl get pods -n litellm
   ```

2. Test LiteLLM directly:
   ```bash
   kubectl exec -it -n litellm deployment/litellm-ui -- curl http://litellm:4000/health
   ```

3. Check the LITELLM_URL environment variable:
   ```bash
   kubectl get configmap litellm-ui-config -n litellm -o yaml
   ```

### Image pull errors

- Verify the image exists in the registry
- Check image pull secrets if using a private registry
- For OpenShift internal registry, ensure the service account has access

### UI not loading

1. Check pod logs:
   ```bash
   kubectl logs -n litellm -l app.kubernetes.io/name=litellm-ui
   ```

2. Check pod status:
   ```bash
   kubectl describe pod -n litellm -l app.kubernetes.io/name=litellm-ui
   ```

## Contributing

1. Make changes to the code
2. Test locally
3. Update documentation if needed
4. Rebuild and redeploy

## License

See parent project license.

