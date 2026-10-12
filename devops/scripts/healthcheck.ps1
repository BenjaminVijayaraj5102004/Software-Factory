# ==============================================================================
# Multi-Service Health Probe & Smoke Test Script (PowerShell / Windows)
# ==============================================================================

param(
    [string]$GatewayHost = "http://localhost",
    [string]$BackendHost = "http://localhost:8000"
)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host " Running Todo Application Health Smoke Tests" -ForegroundColor Cyan
Write-Host " Gateway: $GatewayHost"
Write-Host " Backend: $BackendHost"
Write-Host "==================================================" -ForegroundColor Cyan

function Test-Endpoint {
    param([string]$Url, [string]$Name)
    try {
        $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200 -or $response.StatusCode -eq 304) {
            Write-Host "  [PASS] $Name: HTTP $($response.StatusCode)" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  [FAIL] $Name: HTTP $($response.StatusCode)" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  [FAIL] $Name: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

$backendSuccess = Test-Endpoint -Url "$BackendHost/api/v1/health" -Name "Backend API (/api/v1/health)"
$gatewaySuccess = Test-Endpoint -Url "$GatewayHost/gateway-health" -Name "Nginx Gateway (/gateway-health)"
$frontendSuccess = Test-Endpoint -Url "$GatewayHost/" -Name "Frontend UI ($GatewayHost/)"

Write-Host "==================================================" -ForegroundColor Cyan
if ($backendSuccess -and $gatewaySuccess -and $frontendSuccess) {
    Write-Host " All Service Probes Passed Successfully!" -ForegroundColor Green
    exit 0
} else {
    Write-Host " Some Probes Failed. Review logs with 'docker compose logs'." -ForegroundColor Yellow
    exit 1
}
