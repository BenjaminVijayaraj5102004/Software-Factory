#!/usr/bin/env bash
# ==============================================================================
# Multi-Service Health Probe & Smoke Test Script (Linux / macOS / Bash)
# ==============================================================================

set -euo pipefail

GATEWAY_HOST="${1:-http://localhost}"
BACKEND_HOST="${2:-http://localhost:8000}"

echo "=================================================="
echo " Running Todo Application Health Smoke Tests"
echo " Gateway: $GATEWAY_HOST"
echo " Backend: $BACKEND_HOST"
echo "=================================================="

# Check Backend API Health probe
echo -n "Checking Backend Health (/api/v1/health)... "
BACKEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_HOST/api/v1/health" || echo "000")
if [ "$BACKEND_CODE" -eq 200 ]; then
    echo "OK (HTTP $BACKEND_CODE)"
else
    echo "FAIL (HTTP $BACKEND_CODE)"
fi

# Check Gateway Health probe
echo -n "Checking Gateway Status ($GATEWAY_HOST/gateway-health)... "
GATEWAY_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_HOST/gateway-health" || echo "000")
if [ "$GATEWAY_CODE" -eq 200 ]; then
    echo "OK (HTTP $GATEWAY_CODE)"
else
    echo "FAIL (HTTP $GATEWAY_CODE)"
fi

# Check Frontend Gateway Routing
echo -n "Checking Frontend UI via Gateway ($GATEWAY_HOST/)... "
FRONTEND_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$GATEWAY_HOST/" || echo "000")
if [ "$FRONTEND_CODE" -eq 200 ] || [ "$FRONTEND_CODE" -eq 304 ]; then
    echo "OK (HTTP $FRONTEND_CODE)"
else
    echo "FAIL (HTTP $FRONTEND_CODE)"
fi

echo "=================================================="
echo "Health Checks Finished."
