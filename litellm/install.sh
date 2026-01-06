#!/bin/bash
#
# LiteLLM Installation Script for OpenShift
# Usage: ./install.sh [NAMESPACE]
#

set -e

# Configuration
NAMESPACE="${1:-hacohen-llmlite}"
RELEASE_NAME="litellm"
HELM_CHART="./helm"

echo "============================================"
echo "LiteLLM Installation Script"
echo "============================================"
echo "Namespace: ${NAMESPACE}"
echo ""

# Check prerequisites
command -v oc >/dev/null 2>&1 || { echo "Error: 'oc' command not found. Please install OpenShift CLI."; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "Error: 'helm' command not found. Please install Helm 3."; exit 1; }

# Verify OpenShift connection
echo "Checking OpenShift connection..."
oc whoami || { echo "Error: Not logged into OpenShift. Run 'oc login' first."; exit 1; }
echo ""

# Step 1: Create namespace
echo "[1/2] Creating namespace '${NAMESPACE}'..."
oc create namespace "${NAMESPACE}" --dry-run=client -o yaml | oc apply -f -
echo ""

# Step 2: Deploy with Helm
echo "[2/2] Deploying LiteLLM with Helm..."
helm upgrade --install "${RELEASE_NAME}" "${HELM_CHART}" \
    --namespace "${NAMESPACE}" \
    --set ui.enabled=true \
    --set ui.image.repository=quay.io/rh-ee-rjjohnso/test \
    --set ui.image.tag=latest \
    --wait

echo ""
echo "============================================"
echo "Installation Complete!"
echo "============================================"
echo ""

# Display status
echo "Pod Status:"
oc get pods -n "${NAMESPACE}"
echo ""

# Display URLs
LITELLM_URL=$(oc get route "${RELEASE_NAME}" -n "${NAMESPACE}" -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not found")
UI_URL=$(oc get route "${RELEASE_NAME}-ui" -n "${NAMESPACE}" -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not found")

echo "Access URLs:"
echo "  LiteLLM API:      https://${LITELLM_URL}"
echo "  LiteLLM Admin UI: https://${LITELLM_URL}/ui"
echo "  Streamlit UI:     https://${UI_URL}"
echo ""
echo "Credentials:"
echo "  LiteLLM Admin: username 'admin', password 'master-key'"
echo "  Streamlit UI:  username 'admin', password 'admin'"
echo ""
