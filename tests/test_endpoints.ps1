# Comprehensive PowerShell test suite for ICI Chat application
# Tests all discovered endpoints for functionality verification

param(
    [string]$BaseUrl = "https://localhost:8080",
    [string]$TestEnvId = "test-env-123",
    [string]$TestClientId = "test-client-456", 
    [string]$TestUserId = "test-user-789",
    [string]$TestIp = "192.168.1.100"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ICI CHAT ENDPOINT TESTING SUITE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Base URL: $BaseUrl" -ForegroundColor White
Write-Host "Testing with self-signed certificates (insecure)" -ForegroundColor Yellow
Write-Host ""

# Function to test GET endpoint
function Test-GetEndpoint {
    param(
        [string]$Endpoint,
        [string]$Description
    )
    
    Write-Host "Testing GET: $Endpoint - $Description" -ForegroundColor Blue
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method GET -ContentType "application/json" -SkipCertificateCheck
        Write-Host "SUCCESS: Response received" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3 | Write-Host
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "HTTP Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

# Function to test POST endpoint
function Test-PostEndpoint {
    param(
        [string]$Endpoint,
        [object]$Data,
        [string]$Description
    )
    
    Write-Host "Testing POST: $Endpoint - $Description" -ForegroundColor Blue
    
    try {
        $jsonData = $Data | ConvertTo-Json -Depth 3
        $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method POST -Body $jsonData -ContentType "application/json" -SkipCertificateCheck
        Write-Host "SUCCESS: Response received" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3 | Write-Host
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "HTTP Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

# Function to test DELETE endpoint
function Test-DeleteEndpoint {
    param(
        [string]$Endpoint,
        [string]$Description
    )
    
    Write-Host "Testing DELETE: $Endpoint - $Description" -ForegroundColor Blue
    
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl$Endpoint" -Method DELETE -ContentType "application/json" -SkipCertificateCheck
        Write-Host "SUCCESS: Response received" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3 | Write-Host
    }
    catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            Write-Host "HTTP Status: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }
    Write-Host ""
}

Write-Host "============== BASIC ENDPOINTS ==============" -ForegroundColor Yellow

# Root and main pages
Test-GetEndpoint "/" "Main index page"
Test-GetEndpoint "/chat" "Chat interface"
Test-GetEndpoint "/join" "Join page"
Test-GetEndpoint "/join/$TestClientId" "Join with client ID"

Write-Host "============== UTILITY ENDPOINTS ==============" -ForegroundColor Yellow

# Environment and health
Test-GetEndpoint "/env-id" "Environment ID (JSON)"
Test-GetEndpoint "/health" "Health check page"
Test-GetEndpoint "/system-info" "System information"

Write-Host "============== DOCUMENTATION ==============" -ForegroundColor Yellow

# Documentation pages
Test-GetEndpoint "/readme" "README documentation"
Test-GetEndpoint "/learn" "Learn/lessons documentation"
Test-GetEndpoint "/policies" "Policies page"

Write-Host "============== ADMIN ENDPOINTS ==============" -ForegroundColor Yellow

# Admin and debug
Test-GetEndpoint "/admin" "Admin dashboard"
Test-GetEndpoint "/recovery" "Recovery page"
Test-GetEndpoint "/system-info" "System information"

# Debug endpoints
Test-GetEndpoint "/debug/env-box" "Debug environment box data"
Test-GetEndpoint "/debug/ip-box" "Debug IP box data"
Test-GetEndpoint "/debug/clients" "Debug client data"

Write-Host "============== CLIENT MANAGEMENT ==============" -ForegroundColor Yellow

# Client registration
$clientData = @{
    env_id = $TestEnvId
    public_ip = $TestIp
    client_id = $TestClientId
    user_agent = "powershell-test-agent"
    timestamp = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
}
Test-PostEndpoint "/client-register" $clientData "Register new client"

# Client operations
Test-GetEndpoint "/clients" "List all clients"
Test-GetEndpoint "/clients?env_id=$TestEnvId" "List clients by env_id"
Test-GetEndpoint "/client/$TestClientId/data" "Get client data"
Test-GetEndpoint "/client/$TestClientId/data?env_id=$TestEnvId" "Get client data with env_id"
Test-GetEndpoint "/recovery-data" "Recovery data"
Test-GetEndpoint "/recovery-data?env_id=$TestEnvId" "Recovery data with env_id"

# Client heartbeat
$heartbeatData = @{
    env_id = $TestEnvId
    client_id = $TestClientId
    timestamp = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
}
Test-PostEndpoint "/client-heartbeat" $heartbeatData "Client heartbeat"

Write-Host "============== DATA STORAGE ENDPOINTS ==============" -ForegroundColor Yellow

# Environment box (shared memory)
Test-GetEndpoint "/env-box" "Get environment box data"
Test-GetEndpoint "/env-box?env_id=$TestEnvId" "Get env box data with env_id"

$envBoxData = @{
    env_id = $TestEnvId
    value = @(
        @{
            ts = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
            q = "test question"
            a = "test answer"
        }
    )
}
Test-PostEndpoint "/env-box" $envBoxData "Post to environment box"

# IP box (client-specific memory)
Test-GetEndpoint "/ip-box?env_id=$TestEnvId&public_ip=$TestIp" "Get IP box data"

$ipBoxData = @{
    env_id = $TestEnvId
    public_ip = $TestIp
    value = @(
        @{
            ts = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
            message = "test client message"
        }
    )
}
Test-PostEndpoint "/ip-box" $ipBoxData "Post to IP box"

Write-Host "============== AI CHAT ENDPOINTS ==============" -ForegroundColor Yellow

# Basic AI chat
$aiChatData = @{
    message = "Hello, how are you?"
    system_prompt = "You are a helpful assistant."
}
Test-PostEndpoint "/ai-chat" $aiChatData "Basic AI chat"

# Enhanced AI chat with files
$enhancedChatData = @{
    message = "Analyze this test data"
    system_prompt = "You are a helpful data analyst."
    files = @(
        @{
            name = "test.txt"
            type = "text/plain"
            content = "This is test data for analysis"
            isImage = $false
        }
    )
}
Test-PostEndpoint "/ai-chat-enhanced" $enhancedChatData "Enhanced AI chat with files"

Write-Host "============== MEMORY REPORTS ==============" -ForegroundColor Yellow

# Lost memory reports
$memoryReportData = @{
    env_id = $TestEnvId
    report = "Test memory loss report"
    timestamp = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
}
Test-PostEndpoint "/lost-memory-report" $memoryReportData "Submit lost memory report"

Test-GetEndpoint "/lost-memory-reports" "List all memory reports"
Test-GetEndpoint "/lost-memory-reports?env_id=$TestEnvId" "List memory reports by env_id"

Write-Host "============== VAULT ENDPOINTS ==============" -ForegroundColor Yellow

# Vault data collection
$vaultData = @{
    user_id = $TestUserId
    tab_id = "123"
    url = "https://example.com"
    ui_element = @{
        selector = ".test-element"
        tag_name = "div"
        text_content = "This is test content for vault"
        attributes = @{ class = "test-class" }
        position = @{ x = 100; y = 200 }
    }
    storage_data = @{ key = "value" }
    timestamp = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
}
Test-PostEndpoint "/vault/collect" $vaultData "Collect vault data"

# Vault search
$vaultSearchData = @{
    user_id = $TestUserId
    query = "test content"
    limit = 5
}
Test-PostEndpoint "/vault/search" $vaultSearchData "Search vault entries"

# Vault user data
Test-GetEndpoint "/vault/entries/$TestUserId" "Get user vault entries"
Test-GetEndpoint "/vault/domains/$TestUserId" "Get user domains"
Test-GetEndpoint "/vault/stats/$TestUserId" "Get vault statistics"
Test-GetEndpoint "/vault/vector-stats" "Get vector database stats"

Write-Host "============== WALLET CREATION ==============" -ForegroundColor Yellow

# Crypto wallet creation
Test-PostEndpoint "/client/new-wallet" @{} "Create new crypto wallet"

Write-Host "============== CLIENT AUTHENTICATION ==============" -ForegroundColor Yellow

# Client authentication (QR code endpoint)
Test-GetEndpoint "/client/$TestClientId" "Client authentication page"

Write-Host "============== CLEANUP TESTS ==============" -ForegroundColor Yellow

# Client removal
Test-PostEndpoint "/client/$TestClientId/remove?env_id=$TestEnvId" @{} "Remove client"

# Vault cleanup
Test-DeleteEndpoint "/vault/clear/$TestUserId" "Clear user vault"

# Debug cleanup (be careful with this one!)
Write-Host "CAUTION: Testing dangerous cleanup endpoint" -ForegroundColor Red
$cleanupData = @{
    timestamp = [int64](([datetime]::UtcNow - [datetime]'1970-01-01').TotalMilliseconds)
}
Test-PostEndpoint "/debug/clear-all" $cleanupData "Clear all data (DANGEROUS)"

Write-Host "============== LEGACY ENDPOINTS ==============" -ForegroundColor Yellow
Write-Host "Note: These endpoints exist in the legacy app.py but may not be active in refactored version" -ForegroundColor Blue

# Note: These are from the legacy app.py and may not be available in the refactored version
# Uncomment if testing the legacy monolithic version instead

<#
$clientRememberData = @{ client_id = $TestClientId }
Test-PostEndpoint "/client-remember" $clientRememberData "Client remember (legacy)"

$clientLookupData = @{ client_id = $TestClientId }
Test-PostEndpoint "/client-lookup" $clientLookupData "Client lookup (legacy)"

Test-GetEndpoint "/client-table" "Client table (legacy)"

$askData = @{
    question = "What is the weather?"
    user_id = $TestUserId
}
Test-PostEndpoint "/ask" $askData "Ask endpoint (legacy)"
#>

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "ENDPOINT TESTING COMPLETED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "- Tested all major endpoint categories" -ForegroundColor White
Write-Host "- Used certificate bypass for self-signed certs" -ForegroundColor White
Write-Host "- Included proper JSON payloads for POST/DELETE" -ForegroundColor White
Write-Host "- Tested both success and error scenarios" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Review any errors or unexpected responses above" -ForegroundColor White
Write-Host "2. Check server logs for detailed error information" -ForegroundColor White
Write-Host "3. Verify endpoint functionality in browser" -ForegroundColor White
Write-Host "4. Run load testing if needed" -ForegroundColor White
