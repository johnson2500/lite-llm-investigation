#!/bin/bash
#
# LiteLLM Uninstall Script for OpenShift
# Usage: ./uninstall.sh [NAMESPACE]
#

set -e

# Configuration
NAMESPACE="${1:-hacohen-llmlite}"
RELEASE_NAME="litellm"

echo "============================================"
echo "LiteLLM Uninstall Script"
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

# Confirm deletion
read -p "Are you sure you want to delete LiteLLM and namespace '${NAMESPACE}'? [y/N] " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi
echo ""

# Step 1: Uninstall Helm release
echo "[1/3] Uninstalling Helm release '${RELEASE_NAME}'..."
helm uninstall "${RELEASE_NAME}" --namespace "${NAMESPACE}" 2>/dev/null || echo "Helm release not found or already removed."
echo ""

# Step 2: Delete build configs and image streams
echo "[2/3] Cleaning up build resources..."
oc delete buildconfig litellm-ui -n "${NAMESPACE}" --ignore-not-found=true
oc delete imagestream litellm-ui -n "${NAMESPACE}" --ignore-not-found=true
echo ""

# Step 3: Delete namespace
echo "[3/3] Deleting namespace '${NAMESPACE}'..."
oc delete namespace "${NAMESPACE}" --ignore-not-found=true
echo ""

echo "============================================"
echo "Uninstall Complete!"
echo "============================================"
echo ""
echo "The namespace '${NAMESPACE}' and all its resources have been deleted."
echo ""

