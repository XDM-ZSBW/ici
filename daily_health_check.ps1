#!/usr/bin/env pwsh
# ICI Chat - Daily Health Check Script
# Quick validation of essential endpoints

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ICI CHAT - DAILY HEALTH CHECK" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = "https://localhost:8080"
$errorCount = 0

function Test-Endpoint {
    param(
        [string]$Method = "GET",
        [string]$Endpoint,
        [string]$Description,
        [string]$Body = $null,
        [hashtable]$Headers = @{}
    )
    
    Write-Host "Testing: $Description" -NoNewline
    
    try {
        $uri = "$baseUrl$Endpoint"
        $params = @{
            Uri = $uri
            Method = $Method
            SkipCertificateCheck = $true
            TimeoutSec = 10
        }
        
        if ($Body) {
            $params.Body = $Body
            $params.ContentType = "application/json"
        }
        
        if ($Headers.Count -gt 0) {
            $params.Headers = $Headers
        }
        
        $response = Invoke-RestMethod @params
        Write-Host " ✅ PASS" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host " ❌ FAIL - $($_.Exception.Message)" -ForegroundColor Red
        $script:errorCount++
        return $false
    }
}

# Core system health
Write-Host "=== CORE SYSTEM HEALTH ===" -ForegroundColor Yellow
Test-Endpoint -Endpoint "/env-id" -Description "Environment ID"
Test-Endpoint -Endpoint "/system-info" -Description "System Information"
Test-Endpoint -Endpoint "/health" -Description "Health Check"

Write-Host ""

# Main application pages
Write-Host "=== MAIN APPLICATION ===" -ForegroundColor Yellow
Test-Endpoint -Endpoint "/" -Description "Home Page"
Test-Endpoint -Endpoint "/chat" -Description "Chat Interface"
Test-Endpoint -Endpoint "/admin" -Description "Admin Dashboard"

Write-Host ""

# AI functionality
Write-Host "=== AI FUNCTIONALITY ===" -ForegroundColor Yellow
$aiPayload = '{"message": "Hello", "system_prompt": "You are a helpful assistant."}'
Test-Endpoint -Method "POST" -Endpoint "/ai-chat" -Description "AI Chat" -Body $aiPayload

Write-Host ""

# Memory system
Write-Host "=== MEMORY SYSTEM ===" -ForegroundColor Yellow
Test-Endpoint -Endpoint "/env-box?env_id=health-check" -Description "Memory Retrieval"
$memoryPayload = '{"env_id": "health-check", "value": [{"q": "test", "a": "working", "ts": ' + [DateTimeOffset]::Now.ToUnixTimeMilliseconds() + '}]}'
Test-Endpoint -Method "POST" -Endpoint "/env-box" -Description "Memory Storage" -Body $memoryPayload

Write-Host ""

# Client management
Write-Host "=== CLIENT MANAGEMENT ===" -ForegroundColor Yellow
Test-Endpoint -Endpoint "/clients" -Description "Client List"
$clientPayload = '{"client_id": "health-check-client", "env_id": "health-check", "public_ip": "127.0.0.1"}'
Test-Endpoint -Method "POST" -Endpoint "/client-register" -Description "Client Registration" -Body $clientPayload

Write-Host ""

# Vault system
Write-Host "=== VAULT SYSTEM ===" -ForegroundColor Yellow
Test-Endpoint -Endpoint "/vault/vector-stats" -Description "Vault Statistics"

Write-Host ""

# Results summary
Write-Host "========================================" -ForegroundColor Cyan
if ($errorCount -eq 0) {
    Write-Host "✅ ALL TESTS PASSED - System is healthy!" -ForegroundColor Green
    Write-Host "Server is ready for production use." -ForegroundColor Green
} elseif ($errorCount -le 2) {
    Write-Host "⚠️  MINOR ISSUES DETECTED ($errorCount errors)" -ForegroundColor Yellow
    Write-Host "Most functionality working, check specific failures above." -ForegroundColor Yellow
} else {
    Write-Host "❌ MULTIPLE FAILURES DETECTED ($errorCount errors)" -ForegroundColor Red
    Write-Host "System may not be functioning properly. Check server logs." -ForegroundColor Red
}
Write-Host "========================================" -ForegroundColor Cyan

# Return appropriate exit code
if ($errorCount -eq 0) {
    exit 0
} else {
    exit 1
}
