# LiteLLM Helm Chart

This Helm chart deploys LiteLLM proxy service with optional Streamlit UI on Kubernetes/OpenShift.

## Prerequisites

- Kubernetes 1.19+ or OpenShift 4.x
- Helm 3.0+

## Features

- ✅ LiteLLM proxy service for unified LLM API access
- ✅ Optional Streamlit UI for browsing and testing models
- ✅ PostgreSQL (pgvector) for persistence
- ✅ OpenShift Route support (auto-generated hostnames)
- ✅ Kubernetes Ingress support
- ✅ Configurable model endpoints
- ✅ Health checks and auto-scaling ready

## Quick Start

### Deploy LiteLLM Only

```bash
helm install litellm . \
  --namespace litellm \
  --create-namespace
```

### Deploy LiteLLM + UI

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
echo "LiteLLM UI:  https://$LITELLM_URL/ui"

# Streamlit UI (if enabled)
UI_URL=$(oc get route litellm-ui -n litellm -o jsonpath='{.spec.host}')
echo "Streamlit UI: https://$UI_URL"

# Test the API
curl https://$LITELLM_URL/health
```

## Configuration

### LiteLLM Proxy Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `ghcr.io/berriai/litellm-non_root` |
| `image.tag` | Image tag | `main-latest` |
| `service.port` | Service port | `4000` |
| `litellm.debug` | Enable debug mode | `true` |
| `litellm.masterKey` | Master key for admin UI | `master-key` |
| `litellm.config` | LiteLLM model configuration | See values.yaml |
| `route.enabled` | Enable OpenShift Route | `true` |
| `ingress.enabled` | Enable Kubernetes Ingress | `false` |

### Streamlit UI Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ui.enabled` | Enable UI deployment | `true` |
| `ui.replicaCount` | Number of UI replicas | `1` |
| `ui.image.repository` | UI image repository | `quay.io/rh-ee-rjjohnso/test` |
| `ui.image.tag` | UI image tag | `latest` |
| `ui.service.port` | UI service port | `8501` |
| `ui.route.enabled` | Enable OpenShift Route for UI | `true` |

### PostgreSQL (pgvector) Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `pgvector.enabled` | Enable PostgreSQL | `true` |
| `pgvector.secret.user` | Database user | `postgres` |
| `pgvector.secret.password` | Database password | `litellm_password` |
| `pgvector.secret.dbname` | Database name | `litellm` |

## Customizing Configuration

### Configure LiteLLM Models

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
          model: anthropic/claude-3-opus-20240229
          api_key: your-api-key
      - model_name: llama3
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama:11434
```

### Deploy Without UI

```yaml
ui:
  enabled: false
```

### Enable Ingress (Kubernetes)

```yaml
route:
  enabled: false

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: litellm.example.com
      paths:
        - path: /
          pathType: Prefix
```

## Quick Deployment with Makefile

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
```

## Notes

- The LiteLLM admin UI is available at `/ui` on the main LiteLLM route
- Login with username `admin` and your `masterKey` as password
- The Streamlit UI automatically connects to LiteLLM via internal service discovery
- Changes to the config trigger automatic pod restarts (via checksum annotation)
