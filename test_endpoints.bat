@echo off
REM Comprehensive curl test commands for ICI Chat application
REM Save these commands to individual .bat files or run manually

echo ========================================
echo ICI CHAT ENDPOINT TESTING SUITE (CURL)
echo ========================================
echo Base URL: https://localhost:8080
echo Testing with self-signed certificates (insecure)
echo.

REM Set test variables
set BASE_URL=https://localhost:8080
set TEST_ENV_ID=test-env-123
set TEST_CLIENT_ID=test-client-456
set TEST_USER_ID=test-user-789
set TEST_IP=192.168.1.100

echo ============== BASIC ENDPOINTS ==============

echo Testing GET: / - Main index page
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/"
echo.

echo Testing GET: /chat - Chat interface
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/chat"
echo.

echo Testing GET: /join - Join page
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/join"
echo.

echo ============== UTILITY ENDPOINTS ==============

echo Testing GET: /env-id - Environment ID (JSON)
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/env-id"
echo.

echo Testing GET: /health - Health check page
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/health"
echo.

echo Testing GET: /data - Secure key generation
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/data"
echo.

echo ============== DOCUMENTATION ==============

echo Testing GET: /readme - README documentation
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/readme"
echo.

echo Testing GET: /learn - Learn/lessons documentation
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/learn"
echo.

echo ============== ADMIN ENDPOINTS ==============

echo Testing GET: /admin - Admin dashboard
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/admin"
echo.

echo Testing GET: /system-info - System information
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/system-info"
echo.

echo Testing GET: /debug/env-box - Debug environment box data
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/debug/env-box"
echo.

echo ============== CLIENT MANAGEMENT ==============

echo Testing POST: /client-register - Register new client
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"env_id\":\"%TEST_ENV_ID%\",\"public_ip\":\"%TEST_IP%\",\"client_id\":\"%TEST_CLIENT_ID%\",\"user_agent\":\"curl-test-agent\",\"timestamp\":1640995200000}" "%BASE_URL%/client-register"
echo.

echo Testing GET: /clients - List all clients
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/clients"
echo.

echo Testing POST: /client-heartbeat - Client heartbeat
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"env_id\":\"%TEST_ENV_ID%\",\"client_id\":\"%TEST_CLIENT_ID%\",\"timestamp\":1640995200000}" "%BASE_URL%/client-heartbeat"
echo.

echo ============== DATA STORAGE ENDPOINTS ==============

echo Testing GET: /env-box - Get environment box data
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/env-box"
echo.

echo Testing POST: /env-box - Post to environment box
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"env_id\":\"%TEST_ENV_ID%\",\"value\":[{\"ts\":1640995200000,\"q\":\"test question\",\"a\":\"test answer\"}]}" "%BASE_URL%/env-box"
echo.

echo ============== AI CHAT ENDPOINTS ==============

echo Testing POST: /ai-chat - Basic AI chat
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"message\":\"Hello, how are you?\",\"system_prompt\":\"You are a helpful assistant.\"}" "%BASE_URL%/ai-chat"
echo.

echo Testing POST: /ai-chat-enhanced - Enhanced AI chat with files
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"message\":\"Analyze this test data\",\"system_prompt\":\"You are a helpful data analyst.\",\"files\":[{\"name\":\"test.txt\",\"type\":\"text/plain\",\"content\":\"This is test data for analysis\",\"isImage\":false}]}" "%BASE_URL%/ai-chat-enhanced"
echo.

echo ============== MEMORY REPORTS ==============

echo Testing POST: /lost-memory-report - Submit lost memory report
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"env_id\":\"%TEST_ENV_ID%\",\"report\":\"Test memory loss report\",\"timestamp\":1640995200000}" "%BASE_URL%/lost-memory-report"
echo.

echo Testing GET: /lost-memory-reports - List all memory reports
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/lost-memory-reports"
echo.

echo ============== VAULT ENDPOINTS ==============

echo Testing POST: /vault/collect - Collect vault data
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{\"user_id\":\"%TEST_USER_ID%\",\"tab_id\":\"123\",\"url\":\"https://example.com\",\"ui_element\":{\"selector\":\".test-element\",\"tag_name\":\"div\",\"text_content\":\"This is test content for vault\",\"attributes\":{\"class\":\"test-class\"},\"position\":{\"x\":100,\"y\":200}},\"storage_data\":{\"key\":\"value\"},\"timestamp\":1640995200000}" "%BASE_URL%/vault/collect"
echo.

echo Testing GET: /vault/entries/%TEST_USER_ID% - Get user vault entries
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/vault/entries/%TEST_USER_ID%"
echo.

echo Testing GET: /vault/stats/%TEST_USER_ID% - Get vault statistics
curl -k -s -w "HTTP Status: %%{http_code}\n" -H "Content-Type: application/json" "%BASE_URL%/vault/stats/%TEST_USER_ID%"
echo.

echo ============== WALLET CREATION ==============

echo Testing POST: /client/new-wallet - Create new crypto wallet
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{}" "%BASE_URL%/client/new-wallet"
echo.

echo ============== CLEANUP TESTS ==============

echo Testing POST: /client/%TEST_CLIENT_ID%/remove - Remove client
curl -k -s -w "HTTP Status: %%{http_code}\n" -X POST -H "Content-Type: application/json" -d "{}" "%BASE_URL%/client/%TEST_CLIENT_ID%/remove?env_id=%TEST_ENV_ID%"
echo.

echo Testing DELETE: /vault/clear/%TEST_USER_ID% - Clear user vault
curl -k -s -w "HTTP Status: %%{http_code}\n" -X DELETE -H "Content-Type: application/json" "%BASE_URL%/vault/clear/%TEST_USER_ID%"
echo.

echo ========================================
echo ENDPOINT TESTING COMPLETED
echo ========================================
echo.
echo Summary:
echo - Tested all major endpoint categories
echo - Used self-signed certificate bypass (-k flag)
echo - Included proper JSON payloads for POST/DELETE
echo - Tested both success and error scenarios
echo.
echo Next steps:
echo 1. Review any HTTP 4xx/5xx responses above
echo 2. Check server logs for detailed error information
echo 3. Verify endpoint functionality in browser
echo 4. Run load testing if needed

pause
