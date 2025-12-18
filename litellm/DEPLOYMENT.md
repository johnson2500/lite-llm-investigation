# LiteLLM Unified Deployment Guide

Complete guide for deploying LiteLLM proxy with Streamlit UI using a single Helm chart.

## Overview

This deployment includes:
- **LiteLLM Proxy** - Unified API for multiple LLM providers
- **Streamlit UI** - Web interface for browsing and testing models
- **OpenShift Routes** - Auto-generated URLs for both services

## Quick Start

### 1. Build the UI Image

```bash
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/apps/ui

# For OpenShift
oc new-build --name litellm-ui --binary --strategy docker -n litellm
oc start-build litellm-ui --from-dir=. --follow -n litellm

# OR for Docker/Podman with external registry
podman build -t quay.io/your-org/litellm-ui:latest -f Containerfile .
podman push quay.io/your-org/litellm-ui:latest
```

### 2. Deploy Everything

```bash
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/litellm

# Simple one-command deployment
make install

# Or with custom settings
make install NAMESPACE=my-litellm UI_IMAGE_TAG=v1.0.0
```

### 3. Access the Services

```bash
# Get the routes
oc get routes -n litellm

# Get URLs
LITELLM_API=$(oc get route litellm -n litellm -o jsonpath='{.spec.host}')
UI_URL=$(oc get route litellm-ui -n litellm -o jsonpath='{.spec.host}')

echo "LiteLLM API: https://$LITELLM_API"
echo "UI:          https://$UI_URL"

# Test the API
curl https://$LITELLM_API/health

# Open UI in browser
open "https://$UI_URL"
```

## Configuration Options

### Deploy LiteLLM Only (No UI)

```bash
helm install litellm . \
  --namespace litellm \
  --create-namespace \
  --set ui.enabled=false
```

### Custom Configuration

Create a `custom-values.yaml`:

```yaml
litellm:
  debug: true
  config:
    model_list:
      - model_name: gpt-4
        litellm_params:
          model: azure/gpt-4
          api_base: https://your-endpoint.openai.azure.com/
          api_key: ${AZURE_API_KEY}
      - model_name: llama3
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama:11434

ui:
  enabled: true
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

Deploy with:

```bash
helm install litellm . -f custom-values.yaml --namespace litellm --create-namespace
```

### Enable Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## Makefile Commands

The Makefile provides simple commands for all operations:

```bash
# Show all available commands
make help

# Install everything (builds UI and deploys both services)
make install

# Install only LiteLLM API (no UI)
make install-api-only

# Uninstall
make uninstall

# Check status
make status

# View logs
make logs
make logs-api
make logs-ui

# Get service URLs
make urls

# Test the API
make test

# Complete cleanup (uninstall + delete namespace)
make clean
```

### Makefile Variables

You can customize the deployment with variables:

```bash
# Custom namespace
make install NAMESPACE=my-litellm

# Custom image repository
make install UI_IMAGE_REPO=quay.io/myorg/litellm-ui

# Custom image tag
make install UI_IMAGE_TAG=v1.0.0

# Combine multiple variables
make install NAMESPACE=production UI_IMAGE_TAG=stable
```

## Updating

### Update LiteLLM Configuration

```bash
# Edit helm/values.yaml

# Apply changes
helm upgrade litellm . --namespace litellm
```

### Update UI Code

```bash
cd ../apps/ui

# Make changes to main.py

# Rebuild image
oc start-build litellm-ui --from-dir=. --follow -n litellm

# Restart deployment
kubectl rollout restart deployment/litellm-ui -n litellm
```

### Upgrade Helm Release

```bash
helm upgrade litellm . \
  --namespace litellm \
  -f custom-values.yaml
```

## Monitoring

### Check Status

```bash
# All resources
kubectl get all -n litellm

# Specific components
kubectl get deployment,svc,route -n litellm

# Pod status
kubectl get pods -n litellm -w
```

### View Logs

```bash
# LiteLLM logs
kubectl logs -n litellm -l app.kubernetes.io/name=litellm -f

# UI logs
kubectl logs -n litellm -l app.kubernetes.io/component=ui -f

# All logs
kubectl logs -n litellm --all-containers -f
```

### Describe Resources

```bash
# Deployments
kubectl describe deployment litellm -n litellm
kubectl describe deployment litellm-ui -n litellm

# Routes
oc describe route litellm -n litellm
oc describe route litellm-ui -n litellm
```

## Troubleshooting

### UI Cannot Connect to LiteLLM

```bash
# Check ConfigMap
kubectl get configmap litellm-ui-config -n litellm -o yaml

# Test from UI pod
kubectl exec -it -n litellm deployment/litellm-ui -- sh
curl http://litellm:4000/health

# Verify service
kubectl get svc litellm -n litellm
```

### Image Pull Errors

```bash
# For OpenShift internal registry, ensure build completed
oc get build -n litellm
oc logs -f build/litellm-ui-1 -n litellm

# For external registry, check image pull secrets
kubectl get secret -n litellm
```

### Pods Not Starting

```bash
# Check events
kubectl get events -n litellm --sort-by='.lastTimestamp'

# Describe pod
kubectl describe pod -n litellm <pod-name>

# Check logs
kubectl logs -n litellm <pod-name>
```

## Cleanup

### Remove Everything

```bash
# Uninstall Helm release
helm uninstall litellm --namespace litellm

# Delete namespace
kubectl delete namespace litellm
```

### Remove Only UI

```bash
helm upgrade litellm . \
  --namespace litellm \
  --set ui.enabled=false
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Kubernetes Namespace            │
│              (litellm)                  │
│                                         │
│  ┌──────────────┐    ┌──────────────┐ │
│  │   LiteLLM    │    │  UI (8501)   │ │
│  │   (4000)     │◄───│  Streamlit   │ │
│  └──────┬───────┘    └──────┬───────┘ │
│         │                    │         │
│    ┌────▼────┐          ┌───▼────┐    │
│    │ Service │          │Service │    │
│    └────┬────┘          └───┬────┘    │
│         │                   │          │
│    ┌────▼────┐         ┌───▼────┐     │
│    │  Route  │         │ Route  │     │
│    └────┬────┘         └───┬────┘     │
└─────────┼──────────────────┼──────────┘
          │                  │
     https://litellm    https://ui
          │                  │
    ┌─────▼──────────────────▼─────┐
    │      External Users          │
    └──────────────────────────────┘
```

## Next Steps

1. **Add Authentication**: Configure API keys or OAuth
2. **Add More Models**: Edit `values.yaml` to add model configurations
3. **Set Up Monitoring**: Add Prometheus/Grafana
4. **Configure Autoscaling**: Enable HPA for production
5. **Set Up CI/CD**: Automate builds and deployments
6. **Add Persistent Storage**: For logs and caching

## Support

For issues:
1. Check pod logs: `kubectl logs -n litellm <pod-name>`
2. Check events: `kubectl get events -n litellm`
3. Verify configuration: `helm get values litellm -n litellm`
4. Review documentation: `helm/README.md`

