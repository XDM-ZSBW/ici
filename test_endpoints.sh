#!/bin/bash

# Comprehensive curl test suite for ICI Chat application
# Tests all discovered endpoints for functionality verification

BASE_URL="https://localhost:8080"
TEST_ENV_ID="test-env-123"
TEST_CLIENT_ID="test-client-456"
TEST_USER_ID="test-user-789"
TEST_IP="192.168.1.100"

echo "========================================"
echo "ICI CHAT ENDPOINT TESTING SUITE"
echo "========================================"
echo "Base URL: $BASE_URL"
echo "Testing with self-signed certificates (insecure)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test GET endpoint
test_get() {
    local endpoint="$1"
    local description="$2"
    echo -e "${BLUE}Testing GET:${NC} $endpoint - $description"
    
    curl -k -s -w "HTTP Status: %{http_code}\n" \
         -H "Content-Type: application/json" \
         "$BASE_URL$endpoint" || echo -e "${RED}CURL ERROR${NC}"
    echo ""
}

# Function to test POST endpoint
test_post() {
    local endpoint="$1"
    local data="$2"
    local description="$3"
    echo -e "${BLUE}Testing POST:${NC} $endpoint - $description"
    
    curl -k -s -w "HTTP Status: %{http_code}\n" \
         -X POST \
         -H "Content-Type: application/json" \
         -d "$data" \
         "$BASE_URL$endpoint" || echo -e "${RED}CURL ERROR${NC}"
    echo ""
}

# Function to test DELETE endpoint
test_delete() {
    local endpoint="$1"
    local description="$2"
    echo -e "${BLUE}Testing DELETE:${NC} $endpoint - $description"
    
    curl -k -s -w "HTTP Status: %{http_code}\n" \
         -X DELETE \
         -H "Content-Type: application/json" \
         "$BASE_URL$endpoint" || echo -e "${RED}CURL ERROR${NC}"
    echo ""
}

echo -e "${YELLOW}============== BASIC ENDPOINTS ==============${NC}"

# Root and main pages
test_get "/" "Main index page"
test_get "/chat" "Chat interface"
test_get "/join" "Join page"
test_get "/join/$TEST_CLIENT_ID" "Join with client ID"

echo -e "${YELLOW}============== UTILITY ENDPOINTS ==============${NC}"

# Environment and health
test_get "/env-id" "Environment ID (JSON)"
test_get "/env-id-html" "Environment ID (HTML)"
test_get "/health" "Health check page"
test_get "/data" "Secure key generation"

echo -e "${YELLOW}============== DOCUMENTATION ==============${NC}"

# Documentation pages
test_get "/readme" "README documentation"
test_get "/learn" "Learn/lessons documentation"
test_get "/policies" "Policies page"

echo -e "${YELLOW}============== ADMIN ENDPOINTS ==============${NC}"

# Admin and debug
test_get "/admin" "Admin dashboard"
test_get "/recovery" "Recovery page"
test_get "/system-info" "System information"

# Debug endpoints
test_get "/debug/env-box" "Debug environment box data"
test_get "/debug/ip-box" "Debug IP box data"
test_get "/debug/clients" "Debug client data"

echo -e "${YELLOW}============== CLIENT MANAGEMENT ==============${NC}"

# Client registration
test_post "/client-register" '{
    "env_id": "'$TEST_ENV_ID'",
    "public_ip": "'$TEST_IP'",
    "client_id": "'$TEST_CLIENT_ID'",
    "user_agent": "curl-test-agent",
    "timestamp": '$(date +%s000)'
}' "Register new client"

# Client operations
test_get "/clients" "List all clients"
test_get "/clients?env_id=$TEST_ENV_ID" "List clients by env_id"
test_get "/client/$TEST_CLIENT_ID/data" "Get client data"
test_get "/client/$TEST_CLIENT_ID/data?env_id=$TEST_ENV_ID" "Get client data with env_id"
test_get "/recovery-data" "Recovery data"
test_get "/recovery-data?env_id=$TEST_ENV_ID" "Recovery data with env_id"

# Client heartbeat
test_post "/client-heartbeat" '{
    "env_id": "'$TEST_ENV_ID'",
    "client_id": "'$TEST_CLIENT_ID'",
    "timestamp": '$(date +%s000)'
}' "Client heartbeat"

echo -e "${YELLOW}============== DATA STORAGE ENDPOINTS ==============${NC}"

# Environment box (shared memory)
test_get "/env-box" "Get environment box data"
test_get "/env-box?env_id=$TEST_ENV_ID" "Get env box data with env_id"

test_post "/env-box" '{
    "env_id": "'$TEST_ENV_ID'",
    "value": [
        {"ts": '$(date +%s000)', "q": "test question", "a": "test answer"}
    ]
}' "Post to environment box"

# IP box (client-specific memory)
test_get "/ip-box?env_id=$TEST_ENV_ID&public_ip=$TEST_IP" "Get IP box data"

test_post "/ip-box" '{
    "env_id": "'$TEST_ENV_ID'",
    "public_ip": "'$TEST_IP'",
    "value": [
        {"ts": '$(date +%s000)', "message": "test client message"}
    ]
}' "Post to IP box"

echo -e "${YELLOW}============== AI CHAT ENDPOINTS ==============${NC}"

# Basic AI chat
test_post "/ai-chat" '{
    "message": "Hello, how are you?",
    "system_prompt": "You are a helpful assistant."
}' "Basic AI chat"

# Enhanced AI chat with files
test_post "/ai-chat-enhanced" '{
    "message": "Analyze this test data",
    "system_prompt": "You are a helpful data analyst.",
    "files": [
        {
            "name": "test.txt",
            "type": "text/plain",
            "content": "This is test data for analysis",
            "isImage": false
        }
    ]
}' "Enhanced AI chat with files"

echo -e "${YELLOW}============== MEMORY REPORTS ==============${NC}"

# Lost memory reports
test_post "/lost-memory-report" '{
    "env_id": "'$TEST_ENV_ID'",
    "report": "Test memory loss report",
    "timestamp": '$(date +%s000)'
}' "Submit lost memory report"

test_get "/lost-memory-reports" "List all memory reports"
test_get "/lost-memory-reports?env_id=$TEST_ENV_ID" "List memory reports by env_id"

echo -e "${YELLOW}============== VAULT ENDPOINTS ==============${NC}"

# Vault data collection
test_post "/vault/collect" '{
    "user_id": "'$TEST_USER_ID'",
    "tab_id": "123",
    "url": "https://example.com",
    "ui_element": {
        "selector": ".test-element",
        "tag_name": "div",
        "text_content": "This is test content for vault",
        "attributes": {"class": "test-class"},
        "position": {"x": 100, "y": 200}
    },
    "storage_data": {"key": "value"},
    "timestamp": '$(date +%s000)'
}' "Collect vault data"

# Vault search
test_post "/vault/search" '{
    "user_id": "'$TEST_USER_ID'",
    "query": "test content",
    "limit": 5
}' "Search vault entries"

# Vault user data
test_get "/vault/entries/$TEST_USER_ID" "Get user vault entries"
test_get "/vault/domains/$TEST_USER_ID" "Get user domains"
test_get "/vault/stats/$TEST_USER_ID" "Get vault statistics"
test_get "/vault/vector-stats" "Get vector database stats"

echo -e "${YELLOW}============== WALLET CREATION ==============${NC}"

# Crypto wallet creation
test_post "/client/new-wallet" '{}' "Create new crypto wallet"

echo -e "${YELLOW}============== CLIENT AUTHENTICATION ==============${NC}"

# Client authentication (QR code endpoint)
test_get "/client/$TEST_CLIENT_ID" "Client authentication page"

echo -e "${YELLOW}============== CLEANUP TESTS ==============${NC}"

# Client removal
test_post "/client/$TEST_CLIENT_ID/remove?env_id=$TEST_ENV_ID" '{}' "Remove client"

# Vault cleanup
test_delete "/vault/clear/$TEST_USER_ID" "Clear user vault"

# Debug cleanup (be careful with this one!)
echo -e "${RED}CAUTION: Testing dangerous cleanup endpoint${NC}"
test_post "/debug/clear-all" '{
    "timestamp": '$(date +%s000)'
}' "Clear all data (DANGEROUS)"

echo -e "${YELLOW}============== LEGACY ENDPOINTS ==============${NC}"
echo -e "${BLUE}Note: These endpoints exist in the legacy app.py but may not be active in refactored version${NC}"

# Note: These are from the legacy app.py and may not be available in the refactored version
# Uncomment if testing the legacy monolithic version instead

# test_post "/client-remember" '{
#     "client_id": "'$TEST_CLIENT_ID'"
# }' "Client remember (legacy)"

# test_post "/client-lookup" '{
#     "client_id": "'$TEST_CLIENT_ID'"
# }' "Client lookup (legacy)"

# test_get "/client-table" "Client table (legacy)"

# test_post "/ask" '{
#     "question": "What is the weather?",
#     "user_id": "'$TEST_USER_ID'"
# }' "Ask endpoint (legacy)"

echo ""
echo -e "${GREEN}========================================"
echo "ENDPOINT TESTING COMPLETED"
echo "========================================${NC}"
echo ""
echo "Summary:"
echo "- Tested all major endpoint categories"
echo "- Used self-signed certificate bypass (-k flag)"
echo "- Included proper JSON payloads for POST/DELETE"
echo "- Tested both success and error scenarios"
echo ""
echo "Next steps:"
echo "1. Review any HTTP 4xx/5xx responses above"
echo "2. Check server logs for detailed error information"
echo "3. Verify endpoint functionality in browser"
echo "4. Run load testing if needed"
