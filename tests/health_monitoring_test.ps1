# Health Monitoring System Test Script
# Tests the real-time health monitoring functionality added in ICI Chat v1.3.5
# Date: May 27, 2025

param(
    [string]$BaseUrl = "https://localhost:8080",
    [int]$TimeoutSeconds = 10
)

Write-Host "🩺 ICI Chat Health Monitoring System Test" -ForegroundColor Cyan
Write-Host "=" * 50
Write-Host "Base URL: $BaseUrl" -ForegroundColor Yellow
Write-Host "Timeout: $TimeoutSeconds seconds" -ForegroundColor Yellow
Write-Host ""

# Disable SSL certificate validation for local testing
Add-Type @"
using System;
using System.Net;
using System.Net.Security;
using System.Security.Cryptography.X509Certificates;
public class ServerCertificateValidationCallback
{
    public static void Ignore()
    {
        ServicePointManager.ServerCertificateValidationCallback += 
            delegate
            (
                Object obj, 
                X509Certificate certificate, 
                X509Chain chain, 
                SslPolicyErrors errors
            )
            {
                return true;
            };
    }
}
"@
[ServerCertificateValidationCallback]::Ignore()

$TestResults = @()
$SuccessCount = 0
$TotalTests = 0

function Test-Endpoint {
    param(
        [string]$Url,
        [string]$Description,
        [string]$ExpectedContentType = $null,
        [bool]$IsStreaming = $false,
        [int]$StreamTestSeconds = 3
    )
    
    $global:TotalTests++
    Write-Host "Testing: $Description" -ForegroundColor White
    Write-Host "URL: $Url" -ForegroundColor Gray
    
    try {
        if ($IsStreaming) {
            # Special handling for Server-Sent Events
            $request = [System.Net.WebRequest]::Create($Url)
            $request.Method = "GET"
            $request.Timeout = $StreamTestSeconds * 1000
            
            $response = $request.GetResponse()
            $stream = $response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            
            $contentType = $response.ContentType
            Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "   Content-Type: $contentType" -ForegroundColor Green
            
            # Read a few lines to verify streaming
            $startTime = Get-Date
            $linesRead = 0
            while (((Get-Date) - $startTime).TotalSeconds -lt $StreamTestSeconds -and $linesRead -lt 3) {
                $line = $reader.ReadLine()
                if ($line) {
                    $linesRead++
                    if ($line.StartsWith("data:")) {
                        Write-Host "   Sample Data: $($line.Substring(0, [Math]::Min(50, $line.Length)))..." -ForegroundColor Green
                    }
                }
            }
            
            $reader.Close()
            $response.Close()
            
            if ($ExpectedContentType -and $contentType -like "*$ExpectedContentType*") {
                Write-Host "   ✅ PASS: Streaming endpoint working correctly" -ForegroundColor Green
                $global:SuccessCount++
                return @{ Status = "PASS"; Message = "Streaming endpoint working" }
            } elseif (!$ExpectedContentType) {
                Write-Host "   ✅ PASS: Streaming endpoint accessible" -ForegroundColor Green
                $global:SuccessCount++
                return @{ Status = "PASS"; Message = "Streaming endpoint accessible" }
            } else {
                Write-Host "   ❌ FAIL: Expected content type '$ExpectedContentType', got '$contentType'" -ForegroundColor Red
                return @{ Status = "FAIL"; Message = "Wrong content type" }
            }
        } else {
            # Regular HTTP request
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec $TimeoutSeconds -SkipCertificateCheck -ErrorAction Stop
            
            Write-Host "   Status: $($response.StatusCode)" -ForegroundColor Green
            Write-Host "   Content-Type: $($response.Headers['Content-Type'])" -ForegroundColor Green
            Write-Host "   Content Length: $($response.Content.Length) bytes" -ForegroundColor Green
            
            if ($ExpectedContentType -and $response.Headers['Content-Type'] -like "*$ExpectedContentType*") {
                Write-Host "   ✅ PASS: Correct content type" -ForegroundColor Green
                $global:SuccessCount++
                return @{ Status = "PASS"; Message = "Endpoint working correctly" }
            } elseif (!$ExpectedContentType) {
                Write-Host "   ✅ PASS: Endpoint accessible" -ForegroundColor Green
                $global:SuccessCount++
                return @{ Status = "PASS"; Message = "Endpoint accessible" }
            } else {
                Write-Host "   ❌ FAIL: Expected content type '$ExpectedContentType'" -ForegroundColor Red
                return @{ Status = "FAIL"; Message = "Wrong content type" }
            }
        }
    }
    catch {
        Write-Host "   ❌ FAIL: $($_.Exception.Message)" -ForegroundColor Red
        return @{ Status = "FAIL"; Message = $_.Exception.Message }
    }
    
    Write-Host ""
}

# Test health monitoring endpoints
Write-Host "🔄 Testing Health Monitoring Endpoints..." -ForegroundColor Cyan
Write-Host ""

# Test health page (HTML)
$result = Test-Endpoint -Url "$BaseUrl/health" -Description "Health Check Page" -ExpectedContentType "text/html"
$TestResults += @{ Endpoint = "/health"; Result = $result }

# Test Server-Sent Events endpoint
$result = Test-Endpoint -Url "$BaseUrl/events" -Description "Server-Sent Events Stream" -ExpectedContentType "text/event-stream" -IsStreaming $true -StreamTestSeconds 5
$TestResults += @{ Endpoint = "/events"; Result = $result }

# Test admin configuration
$result = Test-Endpoint -Url "$BaseUrl/admin/config" -Description "Admin Configuration Status" -ExpectedContentType "application/json"
$TestResults += @{ Endpoint = "/admin/config"; Result = $result }

# Test secrets health
$result = Test-Endpoint -Url "$BaseUrl/admin/secrets-health" -Description "Secrets Management Health" -ExpectedContentType "application/json"
$TestResults += @{ Endpoint = "/admin/secrets-health"; Result = $result }

# Test admin dashboard
$result = Test-Endpoint -Url "$BaseUrl/admin" -Description "Admin Dashboard" -ExpectedContentType "text/html"
$TestResults += @{ Endpoint = "/admin"; Result = $result }

# Summary
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "=" * 30
Write-Host "Total Tests: $TotalTests" -ForegroundColor White
Write-Host "Passed: $SuccessCount" -ForegroundColor Green
Write-Host "Failed: $($TotalTests - $SuccessCount)" -ForegroundColor Red
Write-Host "Success Rate: $([Math]::Round(($SuccessCount / $TotalTests) * 100, 1))%" -ForegroundColor Yellow

if ($SuccessCount -eq $TotalTests) {
    Write-Host ""
    Write-Host "🎉 All health monitoring tests passed!" -ForegroundColor Green
    Write-Host "The real-time health monitoring system is working correctly." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Some tests failed. Check the output above for details." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Detailed Results:" -ForegroundColor Cyan
foreach ($test in $TestResults) {
    $status = if ($test.Result.Status -eq "PASS") { "✅" } else { "❌" }
    Write-Host "  $status $($test.Endpoint): $($test.Result.Message)" -ForegroundColor White
}

Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "  • Visit $BaseUrl/health to see the live health dashboard" -ForegroundColor White
Write-Host "  • The health page should show real-time status updates every 5 seconds" -ForegroundColor White
Write-Host "  • If the events endpoint is working, you should see 'Healthy' status in the browser" -ForegroundColor White
Write-Host "  • Check browser dev tools Network tab to see Server-Sent Events in action" -ForegroundColor White

return $SuccessCount -eq $TotalTests
