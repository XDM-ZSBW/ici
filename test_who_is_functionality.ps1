# Test script for "Who is [person]?" functionality
# This script tests the enhanced AI memory system

Write-Host "Testing Enhanced AI Memory System - Who is [person]? functionality" -ForegroundColor Green

$baseUrl = "https://localhost:8080"

# Test environment ID
$testEnvId = "test-who-is-demo"

Write-Host "`nStep 1: Adding test data about people to shared memory..." -ForegroundColor Yellow

# Add information about Alice to shared memory
$aliceData = @{
    env_id = $testEnvId
    value = @(
        @{
            text = "Alice is a software engineer who works on AI projects"
            user = "user1"
            timestamp = [int64]((Get-Date).ToUniversalTime() - [datetime]"1970-01-01T00:00:00Z").TotalMilliseconds
        },
        @{
            text = "Alice should go to the meeting at 3pm"
            user = "user2"
            timestamp = [int64]((Get-Date).ToUniversalTime() - [datetime]"1970-01-01T00:00:00Z").TotalMilliseconds
        }
    )
} | ConvertTo-Json -Depth 3

try {
    Write-Host "Adding Alice data to env-box..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/env-box" -Method POST -Body $aliceData -ContentType "application/json" -SkipCertificateCheck
    Write-Host "✓ Alice data added successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to add Alice data: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 2: Adding information about Bob to IP-shared memory..." -ForegroundColor Yellow

# Add information about Bob to IP-shared memory
$bobData = @{
    env_id = $testEnvId
    public_ip = "192.168.1.100"
    value = @(
        @{
            text = "Bob is the team lead for the frontend development team"
            user = "user3"
            timestamp = [int64]((Get-Date).ToUniversalTime() - [datetime]"1970-01-01T00:00:00Z").TotalMilliseconds
        }
    )
} | ConvertTo-Json -Depth 3

try {
    Write-Host "Adding Bob data to ip-box..." -ForegroundColor Cyan
    $response = Invoke-RestMethod -Uri "$baseUrl/ip-box" -Method POST -Body $bobData -ContentType "application/json" -SkipCertificateCheck
    Write-Host "✓ Bob data added successfully" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to add Bob data: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 3: Testing 'Who is Alice?' query..." -ForegroundColor Yellow

$whoIsAliceQuery = @{
    message = "Who is Alice?"
    user_id = "test-user"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/ai-chat-enhanced" -Method POST -Body $whoIsAliceQuery -ContentType "application/json" -SkipCertificateCheck
    
    Write-Host "Question: Who is Alice?" -ForegroundColor Cyan
    Write-Host "AI Response:" -ForegroundColor White
    Write-Host $response.response -ForegroundColor White
    Write-Host "Memory Context Found: $($response.memory_context_found)" -ForegroundColor Magenta
} catch {
    Write-Host "✗ Failed to query about Alice: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 4: Testing 'Who is Bob?' query..." -ForegroundColor Yellow

$whoIsBobQuery = @{
    message = "Who is Bob?"
    user_id = "test-user"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/ai-chat-enhanced" -Method POST -Body $whoIsBobQuery -ContentType "application/json" -SkipCertificateCheck
    
    Write-Host "Question: Who is Bob?" -ForegroundColor Cyan
    Write-Host "AI Response:" -ForegroundColor White
    Write-Host $response.response -ForegroundColor White
    Write-Host "Memory Context Found: $($response.memory_context_found)" -ForegroundColor Magenta
} catch {
    Write-Host "✗ Failed to query about Bob: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nStep 5: Testing 'Who is Charlie?' query (should find no results)..." -ForegroundColor Yellow

$whoIsCharlieQuery = @{
    message = "Who is Charlie?"
    user_id = "test-user"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/ai-chat-enhanced" -Method POST -Body $whoIsCharlieQuery -ContentType "application/json" -SkipCertificateCheck
    
    Write-Host "Question: Who is Charlie?" -ForegroundColor Cyan
    Write-Host "AI Response:" -ForegroundColor White
    Write-Host $response.response -ForegroundColor White
    Write-Host "Memory Context Found: $($response.memory_context_found)" -ForegroundColor Magenta
} catch {
    Write-Host "✗ Failed to query about Charlie: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTesting Complete!" -ForegroundColor Green
