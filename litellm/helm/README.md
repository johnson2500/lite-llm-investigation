# LiteLLM Helm Chart

This Helm chart deploys LiteLLM proxy service with an optional Streamlit UI on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+ or OpenShift 4.x
- Helm 3.0+

## Features

- ✅ LiteLLM proxy service for unified LLM API access
- ✅ Optional Streamlit UI for browsing and testing models
- ✅ OpenShift Route support (auto-generated hostnames)
- ✅ Kubernetes Ingress support
- ✅ Configurable model endpoints
- ✅ Health checks and auto-scaling ready
- ✅ Single deployment for both services

## Quick Start

### Deploy LiteLLM Only

```bash
helm install litellm . \
  --namespace litellm \
  --create-namespace
```

### Deploy LiteLLM + UI (Recommended)

```bash
# Build UI image first (OpenShift)
cd ../../apps/ui
oc new-build --name litellm-ui --binary --strategy docker -n litellm
oc start-build litellm-ui --from-dir=. --follow -n litellm

# Deploy both services
cd ../../litellm/helm
helm install litellm . \
  --namespace litellm \
  --create-namespace \
  --set ui.enabled=true \
  --set ui.image.repository=image-registry.openshift-image-registry.svc:5000/litellm/litellm-ui \
  --set ui.image.tag=latest
```

### Access the Services

```bash
# Get the URLs
oc get route -n litellm

# LiteLLM API
LITELLM_URL=$(oc get route litellm -n litellm -o jsonpath='{.spec.host}')
echo "LiteLLM API: https://$LITELLM_URL"

# UI (if enabled)
UI_URL=$(oc get route litellm-ui -n litellm -o jsonpath='{.spec.host}')
echo "UI: https://$UI_URL"

# Test the API
curl https://$LITELLM_URL/health
```

## Installation

### Install the chart

```bash
# From the helm directory
helm install litellm . --namespace litellm --create-namespace

# Or with custom values
helm install litellm . \
  --namespace litellm \
  --create-namespace \
  --values custom-values.yaml
```

### Upgrade the chart

```bash
helm upgrade litellm . --namespace litellm
```

### Uninstall the chart

```bash
helm uninstall litellm --namespace litellm
```

## Configuration

The following table lists the configurable parameters of the LiteLLM chart and their default values.

### LiteLLM Proxy Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `ghcr.io/berriai/litellm` |
| `image.tag` | Image tag | `v1.80.5-stable` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `4000` |
| `litellm.debug` | Enable debug mode | `true` |
| `litellm.config` | LiteLLM configuration | See values.yaml |
| `route.enabled` | Enable OpenShift Route | `true` |
| `ingress.enabled` | Enable Kubernetes Ingress | `false` |
| `resources` | CPU/Memory resource requests/limits | `{}` |

### Streamlit UI Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ui.enabled` | Enable UI deployment | `true` |
| `ui.replicaCount` | Number of UI replicas | `1` |
| `ui.image.repository` | UI image repository | `quay.io/your-org/litellm-ui` |
| `ui.image.tag` | UI image tag | `latest` |
| `ui.service.port` | UI service port | `8501` |
| `ui.route.enabled` | Enable OpenShift Route for UI | `true` |
| `ui.ingress.enabled` | Enable Kubernetes Ingress for UI | `false` |
| `ui.resources.limits.cpu` | CPU limit | `500m` |
| `ui.resources.limits.memory` | Memory limit | `512Mi` |
| `ui.resources.requests.cpu` | CPU request | `250m` |
| `ui.resources.requests.memory` | Memory request | `256Mi` |

## Customizing Configuration

### Modify the LiteLLM config

You can customize the LiteLLM configuration by modifying the `litellm.config` section in `values.yaml`:

```yaml
litellm:
  debug: true
  config:
    model_list:
      - model_name: gpt-4
        litellm_params:
          model: azure/gpt-4
          api_base: https://your-endpoint.openai.azure.com/
          api_key: your-api-key
      - model_name: claude
        litellm_params:
          model: anthropic/claude-2
          api_key: your-api-key
```

### Deploy Without UI

```yaml
ui:
  enabled: false
```

### Deploy with External UI Image

```yaml
ui:
  enabled: true
  image:
    repository: quay.io/myorg/litellm-ui
    tag: v1.0.0
```

### Enable Ingress (Kubernetes)

```yaml
route:
  enabled: false

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: litellm.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: litellm-tls
      hosts:
        - litellm.example.com

ui:
  route:
    enabled: false
  ingress:
    enabled: true
    hosts:
      - host: litellm-ui.example.com
        paths:
          - path: /
            pathType: Prefix
```

### Set Resource Limits

```yaml
resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

ui:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

## Building the UI Image

Before deploying with `ui.enabled=true`, you need to build the UI container image:

### Using OpenShift Build

```bash
cd ../../apps/ui

# Create build config
oc new-build --name litellm-ui \
  --binary \
  --strategy docker \
  --to litellm-ui:latest \
  -n litellm

# Build the image
oc start-build litellm-ui --from-dir=. --follow -n litellm
```

### Using Podman/Docker

```bash
cd ../../apps/ui

# Build
podman build -t podman pull quay.io/rh-ee-rjjohnso/test -f Containerfile .

# Push
podman push podman pull quay.io/rh-ee-rjjohnso/test
```

## Accessing the Services

### Port-forward (for testing)

```bash
# LiteLLM API
kubectl port-forward -n litellm svc/litellm 4000:4000

# UI
kubectl port-forward -n litellm svc/litellm-ui 8501:8501
```

### Using OpenShift Routes

```bash
# Get routes
oc get routes -n litellm

# Access LiteLLM
LITELLM=$(oc get route litellm -n litellm -o jsonpath='{.spec.host}')
curl https://$LITELLM/health

# Access UI in browser
UI=$(oc get route litellm-ui -n litellm -o jsonpath='{.spec.host}')
open "https://$UI"
```

## Using the API

```bash
# Health check
curl http://localhost:4000/health

# List models
curl http://localhost:4000/models

# Make a chat completion request
curl http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Quick Deployment with Makefile

The easiest way to deploy is using the Makefile:

```bash
cd ..  # Navigate to litellm directory

# Install everything
make install

# Check status
make status

# Get URLs
make urls

# View logs
make logs

# Uninstall
make uninstall
```

See `make help` for all available commands.

## Troubleshooting

### LiteLLM Pod Not Starting

```bash
kubectl describe pod -n litellm -l app.kubernetes.io/name=litellm
kubectl logs -n litellm -l app.kubernetes.io/name=litellm
```

### UI Cannot Connect to LiteLLM

```bash
# Check ConfigMap
kubectl get configmap litellm-ui-config -n litellm -o yaml

# Test connection from UI pod
kubectl exec -it -n litellm deployment/litellm-ui -- curl http://litellm:4000/health

# Check services
kubectl get svc -n litellm
```

### Routes Not Accessible

```bash
# Check routes
oc get routes -n litellm
oc describe route litellm -n litellm
oc describe route litellm-ui -n litellm
```

## Notes

- The UI automatically connects to the LiteLLM service via internal service discovery
- The original `config.yaml` is embedded in `values.yaml` under `litellm.config`
- Changes to the config trigger automatic pod restarts (via checksum annotation)
- Both services share the same service account and namespace
- For production use, consider:
  - Setting appropriate resource limits
  - Enabling horizontal pod autoscaling
  - Using secrets for API keys
  - Enabling ingress/routes with TLS
  - Setting up monitoring and logging

## Examples

### Deploy with Multiple Models

```yaml
litellm:
  config:
    model_list:
      - model_name: gpt-4
        litellm_params:
          model: azure/gpt-4-deployment
          api_base: https://example.openai.azure.com/
          api_version: "2024-02-15-preview"
      - model_name: claude
        litellm_params:
          model: anthropic/claude-3-opus-20240229
      - model_name: llama3-local
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama.ai-models.svc:11434
```

### Deploy with Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

ui:
  replicaCount: 2
```

### Deploy UI Only (LiteLLM elsewhere)

```yaml
# Don't deploy LiteLLM components
replicaCount: 0

ui:
  enabled: true
  # Override the ConfigMap to point to external LiteLLM
  # You'll need to manually create a ConfigMap with LITELLM_URL
```

## Contributing

Issues and pull requests are welcome!

## License

See parent project license.
