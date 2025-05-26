# Test script for the enhanced AI memory system
# This demonstrates the vector database memory functionality

Write-Host "Testing AI Memory System with Vector Database" -ForegroundColor Green

# First, let's ask a question that should retrieve memory
Write-Host "`nStep 1: Testing memory retrieval for Tommy's schedule..." -ForegroundColor Yellow

$questionPayload = @{
    message = "Should Tommy go at 2pm?"
    user_id = "anonymous"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://localhost:8080/ai-chat-enhanced" -Method POST -Body $questionPayload -ContentType "application/json" -SkipCertificateCheck
    
    Write-Host "Question: Should Tommy go at 2pm?" -ForegroundColor Cyan
    Write-Host "AI Response: $($response.response)" -ForegroundColor White
    Write-Host "Memory Context Found: $($response.memory_context_found)" -ForegroundColor Magenta
    Write-Host "Memory Stored: $($response.memory_stored)" -ForegroundColor Magenta
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Let's also test storing new information
Write-Host "`nStep 2: Testing memory storage for new information..." -ForegroundColor Yellow

$storePayload = @{
    message = "Sarah likes pizza on Fridays"
    user_id = "anonymous"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://localhost:8080/ai-chat-enhanced" -Method POST -Body $storePayload -ContentType "application/json" -SkipCertificateCheck
    
    Write-Host "Statement: Sarah likes pizza on Fridays" -ForegroundColor Cyan
    Write-Host "AI Response: $($response.response)" -ForegroundColor White
    Write-Host "Memory Stored: $($response.memory_stored)" -ForegroundColor Magenta
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test retrieval of the new information
Write-Host "`nStep 3: Testing retrieval of Sarah's preference..." -ForegroundColor Yellow

$retrievePayload = @{
    message = "What does Sarah like?"
    user_id = "anonymous"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "https://localhost:8080/ai-chat-enhanced" -Method POST -Body $retrievePayload -ContentType "application/json" -SkipCertificateCheck
    
    Write-Host "Question: What does Sarah like?" -ForegroundColor Cyan
    Write-Host "AI Response: $($response.response)" -ForegroundColor White
    Write-Host "Memory Context Found: $($response.memory_context_found)" -ForegroundColor Magenta
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nMemory system test completed!" -ForegroundColor Green
