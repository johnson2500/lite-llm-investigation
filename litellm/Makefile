.PHONY: help install uninstall build-ui deploy status logs clean upgrade

# Variables
NAMESPACE ?= litellm
RELEASE_NAME ?= litellm
UI_IMAGE_REPO ?= quay.io/rh-ee-rjjohnso/test
UI_IMAGE_TAG ?= latest
HELM_CHART ?= ./helm
UI_SOURCE_DIR ?= ../apps/ui

# Detect OpenShift vs Kubernetes
KUBE_CMD := $(shell command -v oc 2> /dev/null)
ifndef KUBE_CMD
    KUBE_CMD := kubectl
    USE_OPENSHIFT := false
else
    USE_OPENSHIFT := true
endif

help:
	@echo "LiteLLM Deployment Makefile"
	@echo "============================"
	@echo ""
	@echo "Usage:"
	@echo "  make install          - Build UI image and install LiteLLM + UI"
	@echo "  make install-api-only - Install only LiteLLM (no UI)"
	@echo "  make uninstall        - Uninstall LiteLLM and UI"
	@echo "  make build-ui         - Build the UI container image"
	@echo "  make upgrade          - Upgrade existing deployment"
	@echo "  make status           - Show deployment status"
	@echo "  make logs             - Show logs for both services"
	@echo "  make logs-api         - Show LiteLLM API logs"
	@echo "  make logs-ui          - Show UI logs"
	@echo "  make urls             - Display service URLs"
	@echo "  make clean            - Uninstall and delete namespace"
	@echo ""
	@echo "Variables:"
	@echo "  NAMESPACE=$(NAMESPACE)"
	@echo "  RELEASE_NAME=$(RELEASE_NAME)"
	@echo "  UI_IMAGE_REPO=$(UI_IMAGE_REPO)"
	@echo "  UI_IMAGE_TAG=$(UI_IMAGE_TAG)"
	@echo ""
	@echo "Examples:"
	@echo "  make install"
	@echo "  make install NAMESPACE=my-litellm"
	@echo "  make uninstall"
	@echo "  make status"

build-ui:
	@echo "Building UI container image..."
ifeq ($(USE_OPENSHIFT),true)
	@echo "Using OpenShift build..."
	@# Ensure namespace exists before creating build config
	@$(KUBE_CMD) create namespace $(NAMESPACE) --dry-run=client -o yaml | $(KUBE_CMD) apply -f -
	@# Create build config if it doesn't exist (ignore errors if it already exists)
	@cd $(UI_SOURCE_DIR) && \
		oc get buildconfig litellm-ui -n $(NAMESPACE) >/dev/null 2>&1 || \
		oc new-build --name litellm-ui --binary --strategy docker --to litellm-ui:$(UI_IMAGE_TAG) -n $(NAMESPACE)
	@# Start the build
	@cd $(UI_SOURCE_DIR) && \
		oc start-build litellm-ui --from-dir=. --follow -n $(NAMESPACE)
else
	@echo "Using Podman/Docker build..."
	@cd $(UI_SOURCE_DIR) && \
		podman build -t $(UI_IMAGE_REPO):$(UI_IMAGE_TAG) -f Containerfile .
	@echo "Pushing image to registry..."
	@podman push $(UI_IMAGE_REPO):$(UI_IMAGE_TAG)
endif
	@echo "✅ UI image built successfully"

install: build-ui
	@echo "Installing LiteLLM + UI..."
	@$(KUBE_CMD) create namespace $(NAMESPACE) --dry-run=client -o yaml | $(KUBE_CMD) apply -f -
ifeq ($(USE_OPENSHIFT),true)
	@helm upgrade --install $(RELEASE_NAME) $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--set ui.enabled=true \
		--set ui.image.repository=quay.io/rh-ee-rjjohnso/test \
		--set ui.image.tag=$(UI_IMAGE_TAG) \
		--wait
else
	@helm upgrade --install $(RELEASE_NAME) $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--set ui.enabled=true \
		--set ui.image.repository=$(UI_IMAGE_REPO) \
		--set ui.image.tag=$(UI_IMAGE_TAG) \
		--wait
endif
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@$(MAKE) urls

install-api-only:
	@echo "Installing LiteLLM (API only, no UI)..."
	@$(KUBE_CMD) create namespace $(NAMESPACE) --dry-run=client -o yaml | $(KUBE_CMD) apply -f -
	@helm upgrade --install $(RELEASE_NAME) $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--set ui.enabled=false \
		--wait
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@$(MAKE) urls

upgrade:
	@echo "Upgrading LiteLLM deployment..."
	@helm upgrade $(RELEASE_NAME) $(HELM_CHART) \
		--namespace $(NAMESPACE) \
		--wait
	@echo "✅ Upgrade complete!"

uninstall:
	@echo "Uninstalling LiteLLM..."
	@helm uninstall $(RELEASE_NAME) --namespace $(NAMESPACE) || true
	@echo "✅ Uninstalled successfully"

clean: uninstall
	@echo "Deleting namespace..."
	@$(KUBE_CMD) delete namespace $(NAMESPACE) --ignore-not-found=true
	@echo "✅ Cleanup complete"

status:
	@echo "=== Deployment Status ==="
	@echo ""
	@echo "Helm Release:"
	@helm list -n $(NAMESPACE) || true
	@echo ""
	@echo "Pods:"
	@$(KUBE_CMD) get pods -n $(NAMESPACE) || true
	@echo ""
	@echo "Services:"
	@$(KUBE_CMD) get svc -n $(NAMESPACE) || true
	@echo ""
ifeq ($(USE_OPENSHIFT),true)
	@echo "Routes:"
	@oc get routes -n $(NAMESPACE) || true
else
	@echo "Ingresses:"
	@$(KUBE_CMD) get ingress -n $(NAMESPACE) || true
endif

logs:
	@echo "=== LiteLLM API Logs ==="
	@$(KUBE_CMD) logs -n $(NAMESPACE) -l app.kubernetes.io/name=litellm --tail=50 || true
	@echo ""
	@echo "=== UI Logs ==="
	@$(KUBE_CMD) logs -n $(NAMESPACE) -l app.kubernetes.io/component=ui --tail=50 || true

logs-api:
	@$(KUBE_CMD) logs -n $(NAMESPACE) -l app.kubernetes.io/name=litellm -f

logs-ui:
	@$(KUBE_CMD) logs -n $(NAMESPACE) -l app.kubernetes.io/component=ui -f

urls:
	@echo "=== Service URLs ==="
ifeq ($(USE_OPENSHIFT),true)
	@LITELLM_URL=$$(oc get route $(RELEASE_NAME) -n $(NAMESPACE) -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not found"); \
	UI_URL=$$(oc get route $(RELEASE_NAME)-ui -n $(NAMESPACE) -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not found"); \
	if [ "$$LITELLM_URL" != "Not found" ]; then \
		echo "🔌 LiteLLM API: https://$$LITELLM_URL"; \
		echo "   Health:     https://$$LITELLM_URL/health"; \
		echo "   Models:     https://$$LITELLM_URL/models"; \
	else \
		echo "⚠️  LiteLLM route not found"; \
	fi; \
	echo ""; \
	if [ "$$UI_URL" != "Not found" ]; then \
		echo "🌐 UI:          https://$$UI_URL"; \
	else \
		echo "⚠️  UI route not found (UI may be disabled)"; \
	fi
else
	@echo "📝 Use port-forward to access services:"
	@echo "  $(KUBE_CMD) port-forward -n $(NAMESPACE) svc/$(RELEASE_NAME) 4000:4000"
	@echo "  $(KUBE_CMD) port-forward -n $(NAMESPACE) svc/$(RELEASE_NAME)-ui 8501:8501"
	@echo ""
	@echo "Then access:"
	@echo "  LiteLLM API: http://localhost:4000"
	@echo "  UI:          http://localhost:8501"
endif
