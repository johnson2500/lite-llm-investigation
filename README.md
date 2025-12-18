# LiteLLM Investigation & Deployment

Complete deployment package for LiteLLM proxy with Streamlit UI on Kubernetes/OpenShift.

## 🎯 Overview

This project provides a production-ready Helm chart for deploying:
- **LiteLLM Proxy** - Unified API gateway for multiple LLM providers (OpenAI, Azure, Anthropic, Ollama, etc.)
- **Streamlit UI** - Web interface for browsing and testing available models

Both services are deployed together with a single Helm chart for simplified management.

## 🚀 Quick Start

### 1. Build the UI Image

```bash
cd apps/ui

# For OpenShift
oc new-build --name litellm-ui --binary --strategy docker -n litellm
oc start-build litellm-ui --from-dir=. --follow -n litellm

# OR for external registry
podman build -t quay.io/your-org/litellm-ui:latest -f Containerfile .
podman push quay.io/your-org/litellm-ui:latest
```

### 2. Deploy Everything

```bash
cd litellm

# Simple deployment with Makefile
make install

# Or specify custom namespace
make install NAMESPACE=my-litellm
```

### 3. Access Your Services

```bash
# Get the routes
oc get routes -n litellm

# URLs
LITELLM_API=$(oc get route litellm -n litellm -o jsonpath='{.spec.host}')
UI_URL=$(oc get route litellm-ui -n litellm -o jsonpath='{.spec.host}')

echo "LiteLLM API: https://$LITELLM_API"
echo "UI:          https://$UI_URL"

# Test the API
curl https://$LITELLM_API/health
curl https://$LITELLM_API/models

# Open UI in browser
open "https://$UI_URL"
```

## 📁 Project Structure

```
lite-llm-investigation/
├── README.md                          # This file
├── litellm/
│   ├── config.yaml                    # LiteLLM configuration
│   ├── deploy-all.sh                  # Automated deployment script
│   ├── DEPLOYMENT.md                  # Detailed deployment guide
│   └── helm/                          # Unified Helm chart
│       ├── Chart.yaml
│       ├── values.yaml                # Configuration for both services
│       ├── README.md
│       └── templates/
│           ├── deployment.yaml        # LiteLLM deployment
│           ├── service.yaml           # LiteLLM service
│           ├── route.yaml             # LiteLLM route
│           ├── configmap.yaml         # LiteLLM config
│           ├── ui-deployment.yaml     # UI deployment
│           ├── ui-service.yaml        # UI service
│           ├── ui-route.yaml          # UI route
│           ├── ui-configmap.yaml      # UI config
│           └── ...
│
└── apps/
    └── ui/
        ├── main.py                    # Streamlit application
        ├── requirements.txt           # Python dependencies
        ├── Containerfile              # Container image definition
        ├── README.md                  # UI documentation
        └── DEPLOYMENT.md              # Points to main deployment guide
```

## ⚙️ Configuration

### Configure LiteLLM Models

Edit `litellm/helm/values.yaml`:

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
      
      - model_name: claude
        litellm_params:
          model: anthropic/claude-3-opus-20240229
          api_key: ${ANTHROPIC_API_KEY}
      
      - model_name: llama3
        litellm_params:
          model: ollama/llama3
          api_base: http://ollama:11434
```

### Deploy Without UI

```bash
helm install litellm . \
  --namespace litellm \
  --create-namespace \
  --set ui.enabled=false
```

### Custom Resource Limits

```yaml
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 1000m
    memory: 1Gi

ui:
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
    requests:
      cpu: 500m
      memory: 512Mi
```

### Enable Autoscaling

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
```

## 📚 Documentation

- **[Deployment Guide](litellm/DEPLOYMENT.md)** - Complete step-by-step deployment instructions
- **[Helm Chart README](litellm/helm/README.md)** - Helm chart configuration options
- **[UI README](apps/ui/README.md)** - Streamlit UI documentation

## 🔧 Common Operations

### Update Configuration

```bash
cd litellm/helm

# Edit values.yaml with your changes

# Apply updates
helm upgrade litellm . --namespace litellm
```

### Update UI Code

```bash
cd apps/ui

# Make changes to main.py

# Rebuild image
oc start-build litellm-ui --from-dir=. --follow -n litellm

# Restart deployment
kubectl rollout restart deployment/litellm-ui -n litellm
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

### Check Status

```bash
# All resources
kubectl get all -n litellm

# Pods
kubectl get pods -n litellm -w

# Routes (OpenShift)
oc get routes -n litellm
```

## 🐛 Troubleshooting

### UI Cannot Connect to LiteLLM

```bash
# Check ConfigMap
kubectl get configmap litellm-ui-config -n litellm -o yaml

# Test from UI pod
kubectl exec -it -n litellm deployment/litellm-ui -- curl http://litellm:4000/health

# Verify LiteLLM service
kubectl get svc litellm -n litellm
```

### Pods Not Starting

```bash
# Check pod status
kubectl describe pod -n litellm <pod-name>

# Check logs
kubectl logs -n litellm <pod-name>

# Check events
kubectl get events -n litellm --sort-by='.lastTimestamp'
```

### Image Pull Errors

```bash
# For OpenShift builds
oc get builds -n litellm
oc logs -f build/litellm-ui-1 -n litellm

# For external registry
kubectl describe pod -n litellm <pod-name>
```

## 🧹 Cleanup

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

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         Kubernetes/OpenShift Namespace          │
│                  (litellm)                      │
│                                                 │
│  ┌────────────────┐         ┌────────────────┐ │
│  │   LiteLLM      │         │  Streamlit UI  │ │
│  │   Proxy        │◄────────│  (Port 8501)   │ │
│  │  (Port 4000)   │         │                │ │
│  └────────┬───────┘         └───────┬────────┘ │
│           │                         │          │
│      ┌────▼─────┐              ┌───▼─────┐    │
│      │ Service  │              │ Service │    │
│      └────┬─────┘              └───┬─────┘    │
│           │                        │          │
│      ┌────▼─────┐              ┌──▼──────┐    │
│      │  Route   │              │  Route  │    │
│      └────┬─────┘              └───┬─────┘    │
└───────────┼─────────────────────────┼──────────┘
            │                         │
       https://api                https://ui
            │                         │
       ┌────▼─────────────────────────▼─────┐
       │         External Users             │
       │   (Browsers, API Clients)          │
       └────────────────────────────────────┘
            │
            │
       ┌────▼─────────────────────────┐
       │    Backend LLM Providers     │
       │  (OpenAI, Azure, Anthropic,  │
       │   Ollama, etc.)              │
       └──────────────────────────────┘
```

## 🎓 Features

- ✅ **Unified Deployment** - Single Helm chart for both services
- ✅ **Auto-Discovery** - UI automatically connects to LiteLLM service
- ✅ **OpenShift Native** - Routes with auto-generated hostnames
- ✅ **Kubernetes Compatible** - Also supports Ingress
- ✅ **Health Checks** - Liveness and readiness probes
- ✅ **Configurable** - Easy model configuration via values.yaml
- ✅ **Scalable** - Supports horizontal pod autoscaling
- ✅ **Secure** - TLS termination at the route/ingress level

## 📝 API Usage Examples

### List Available Models

```bash
curl https://$LITELLM_API/models
```

### Chat Completion

```bash
curl https://$LITELLM_API/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [
      {"role": "user", "content": "What is Kubernetes?"}
    ]
  }'
```

### Streaming Response

```bash
curl https://$LITELLM_API/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

## 🔐 Security Considerations

- Store API keys in Kubernetes Secrets, not in values.yaml
- Use RBAC to restrict access to namespaces
- Enable network policies to limit pod-to-pod communication
- Use image pull secrets for private registries
- Configure pod security contexts appropriately
- Regularly update base images and dependencies

## 🚦 Next Steps

1. **Add Authentication** - Implement API key validation or OAuth
2. **Set Up Monitoring** - Add Prometheus metrics and Grafana dashboards
3. **Configure Logging** - Centralize logs with ELK or Loki
4. **Add More Models** - Configure additional LLM providers
5. **CI/CD Pipeline** - Automate builds and deployments
6. **Persistent Storage** - Add PVCs for caching if needed
7. **Rate Limiting** - Implement request rate limiting
8. **Cost Tracking** - Add usage metrics and cost monitoring

## 📞 Support

For issues or questions:
1. Check the logs: `kubectl logs -n litellm <pod-name>`
2. Review the deployment guide: [litellm/DEPLOYMENT.md](litellm/DEPLOYMENT.md)
3. Verify configuration: `helm get values litellm -n litellm`
4. Check events: `kubectl get events -n litellm --sort-by='.lastTimestamp'`

## 📄 License

See LICENSE file for details.

---

**Ready to deploy?** Start with the [Quick Start](#-quick-start) section above! 🚀
