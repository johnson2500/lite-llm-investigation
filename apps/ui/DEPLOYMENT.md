# LiteLLM UI Deployment Guide

> **⚠️ Note:** This UI is now deployed as part of the unified LiteLLM Helm chart.
> 
> **Please refer to:** [../../litellm/DEPLOYMENT.md](../../litellm/DEPLOYMENT.md)
>
> The Helm chart has been consolidated into `../../litellm/helm/` for easier deployment of both services together.

---

## Quick Links

- **Main Deployment Guide**: [../../litellm/DEPLOYMENT.md](../../litellm/DEPLOYMENT.md)
- **Helm Chart**: [../../litellm/helm/](../../litellm/helm/)
- **Helm Chart README**: [../../litellm/helm/README.md](../../litellm/helm/README.md)

## Quick Deployment

Complete guide for deploying the LiteLLM Streamlit UI alongside the LiteLLM proxy service.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Streamlit UI  │─────▶│  LiteLLM Proxy   │─────▶│  Ollama/LLMs    │
│   (Port 8501)   │      │   (Port 4000)    │      │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
         │                        │
         │                        │
    ┌────▼────┐              ┌───▼────┐
    │  Route  │              │ Route  │
    │   (UI)  │              │ (API)  │
    └─────────┘              └────────┘
```

## Step-by-Step Deployment

### Step 1: Deploy LiteLLM Proxy

First, deploy the LiteLLM proxy service:

```bash
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/litellm/helm

# Deploy LiteLLM
helm install litellm . --namespace litellm --create-namespace

# Verify deployment
kubectl get pods -n litellm
kubectl get route -n litellm

# Get the LiteLLM API URL
LITELLM_API=$(oc get route litellm -n litellm -o jsonpath='{.spec.host}')
echo "LiteLLM API: https://$LITELLM_API"

# Test the API
curl https://$LITELLM_API/health
```

### Step 2: Build the UI Container Image

```bash
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/apps/ui

# Option A: Build with Podman/Docker
podman build -t quay.io/your-org/litellm-ui:latest -f Containerfile .
podman push quay.io/your-org/litellm-ui:latest

# Option B: Build with OpenShift
oc new-build --name litellm-ui \
  --binary \
  --strategy docker \
  --to litellm-ui:latest \
  -n litellm

oc start-build litellm-ui --from-dir=. --follow -n litellm
```

### Step 3: Deploy the UI

```bash
cd helm

# Deploy UI (using OpenShift internal image)
helm install litellm-ui . \
  --namespace litellm \
  --set image.repository=image-registry.openshift-image-registry.svc:5000/litellm/litellm-ui \
  --set image.tag=latest

# OR deploy UI (using external registry)
helm install litellm-ui . \
  --namespace litellm \
  --set image.repository=quay.io/your-org/litellm-ui \
  --set image.tag=latest

# Verify deployment
kubectl get pods -n litellm
kubectl get route -n litellm
```

### Step 4: Access the UI

```bash
# Get the UI URL
UI_URL=$(oc get route litellm-ui -n litellm -o jsonpath='{.spec.host}')
echo "UI available at: https://$UI_URL"

# Open in browser
open "https://$UI_URL"
```

## Complete Deployment Script

Here's a complete script to deploy everything:

```bash
#!/bin/bash
set -e

NAMESPACE="litellm"
ORG="your-org"

echo "==> Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "==> Deploying LiteLLM proxy..."
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/litellm/helm
helm upgrade --install litellm . --namespace $NAMESPACE

echo "==> Waiting for LiteLLM to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/litellm -n $NAMESPACE

echo "==> Building UI image..."
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/apps/ui

# Using OpenShift build
oc new-build --name litellm-ui \
  --binary \
  --strategy docker \
  --to litellm-ui:latest \
  -n $NAMESPACE 2>/dev/null || true

oc start-build litellm-ui --from-dir=. --follow -n $NAMESPACE

echo "==> Deploying UI..."
cd helm
helm upgrade --install litellm-ui . \
  --namespace $NAMESPACE \
  --set image.repository=image-registry.openshift-image-registry.svc:5000/$NAMESPACE/litellm-ui \
  --set image.tag=latest

echo "==> Waiting for UI to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/litellm-ui -n $NAMESPACE

echo "==> Getting URLs..."
LITELLM_URL=$(oc get route litellm -n $NAMESPACE -o jsonpath='{.spec.host}')
UI_URL=$(oc get route litellm-ui -n $NAMESPACE -o jsonpath='{.spec.host}')

echo ""
echo "✅ Deployment complete!"
echo ""
echo "LiteLLM API: https://$LITELLM_URL"
echo "UI:          https://$UI_URL"
echo ""
echo "Test the API:"
echo "  curl https://$LITELLM_URL/health"
echo ""
echo "Open the UI:"
echo "  open https://$UI_URL"
```

Save this as `deploy.sh`, make it executable, and run:

```bash
chmod +x deploy.sh
./deploy.sh
```

## Configuration Options

### Using External LiteLLM

If LiteLLM is deployed externally or in a different namespace:

```bash
helm install litellm-ui . \
  --namespace litellm-ui \
  --create-namespace \
  --set image.repository=quay.io/your-org/litellm-ui \
  --set image.tag=latest \
  --set litellm.url=https://litellm.example.com
```

### Custom Resource Limits

```bash
helm install litellm-ui . \
  --namespace litellm \
  --set image.repository=quay.io/your-org/litellm-ui \
  --set resources.limits.cpu=1000m \
  --set resources.limits.memory=1Gi \
  --set resources.requests.cpu=500m \
  --set resources.requests.memory=512Mi
```

### Enable Autoscaling

```bash
helm install litellm-ui . \
  --namespace litellm \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --set autoscaling.targetCPUUtilizationPercentage=80
```

## Updating the Application

### Update the Code

```bash
cd /Users/rjjohnso/Documents/code/POC/lite-llm-investigation/apps/ui

# Make changes to main.py

# Rebuild image
oc start-build litellm-ui --from-dir=. --follow -n litellm

# Restart deployment to use new image
kubectl rollout restart deployment/litellm-ui -n litellm

# Watch the rollout
kubectl rollout status deployment/litellm-ui -n litellm
```

### Update Configuration

```bash
cd helm

# Update values.yaml or create a new values file

# Apply changes
helm upgrade litellm-ui . --namespace litellm

# Or with custom values
helm upgrade litellm-ui . --namespace litellm -f custom-values.yaml
```

## Monitoring and Troubleshooting

### View Logs

```bash
# UI logs
kubectl logs -n litellm -l app.kubernetes.io/name=litellm-ui --tail=100 -f

# LiteLLM logs
kubectl logs -n litellm -l app.kubernetes.io/name=litellm --tail=100 -f
```

### Check Status

```bash
# All resources
kubectl get all -n litellm

# Specific resources
kubectl get deployment,service,route -n litellm
```

### Debug Connection Issues

```bash
# Test from UI pod to LiteLLM service
kubectl exec -it -n litellm deployment/litellm-ui -- sh
# Inside pod:
curl http://litellm:4000/health
curl http://litellm:4000/models

# Test from outside
LITELLM_URL=$(oc get route litellm -n litellm -o jsonpath='{.spec.host}')
curl https://$LITELLM_URL/health
curl https://$LITELLM_URL/models
```

## Cleanup

### Remove Everything

```bash
# Uninstall both charts
helm uninstall litellm-ui --namespace litellm
helm uninstall litellm --namespace litellm

# Delete namespace
kubectl delete namespace litellm
```

### Remove Just the UI

```bash
helm uninstall litellm-ui --namespace litellm
```

## Next Steps

1. Configure authentication/authorization
2. Add custom models to LiteLLM config
3. Set up monitoring and alerting
4. Configure persistent storage if needed
5. Set up CI/CD pipelines for automated deployments

