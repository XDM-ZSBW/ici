# 🚀 ICI Chat API Quick Reference - Updated May 27, 2025

## Recent Refactoring Updates
- **File Organization**: Documentation moved to `docs/`, tests moved to `tests/`
- **Security Enhancements**: 256-bit hex client IDs replace legacy wallet-style IDs
- **QR Code Fixes**: Eliminated duplicate QR code display logic
- **Modular Architecture**: Enhanced backend structure with specialized route modules

## Essential Endpoints

### Core System
- `GET /env-id` → Get environment identifier
- `GET /system-info` → Comprehensive server status and Python environment info
- `GET /health` → Health check with live data stream and system diagnostics

### Main Application
- `GET /` → Landing page with navigation and project overview
- `GET /chat` → AI chat interface with secure client ID generation
- `GET /join` → QR authentication and live client session table
- `GET /admin` → Administrative dashboard with real-time statistics
- `GET /learn` → Learning guide for collaborative memory usage
- `GET /readme` → Project documentation and technical specifications
- `GET /changelog` → Version history and feature updates

### Enhanced AI Chat
- `POST /ai-chat` → AI conversation with integrated memory search
  ```json
  {"message": "Who is Sarah?", "user_id": "client_256bit_hex_id"}
  ```
- `POST /ai-chat-enhanced` → AI chat with file uploads and screenshot support
  ```json
  {"message": "Analyze this", "files": [...], "system_prompt": "..."}
  ```

### Advanced Memory System
- `GET /env-box?env_id=xxx` → Get shared memory with cross-environment search
- `POST /env-box` → Store shared memory with timestamp tracking
  ```json
  {"env_id": "xxx", "value": [{"text": "content", "user": "user_id", "timestamp": 123}]}
  ```
- `GET /ip-box?env_id=xxx&public_ip=yyy` → Get IP-scoped shared memory
- `POST /ip-box` → Store IP-specific memory
- `GET /env-box-aggregate` → Cross-environment memory aggregation

### Secure Client Management
- `POST /client-register` → Register client with 256-bit hex ID
  ```json
  {"client_id": "256_bit_hex_string", "env_id": "env", "public_ip": "ip"}
  ```
- `GET /clients` → List all registered clients with session info
- `POST /client-heartbeat` → Update client last-seen timestamp
- `GET /client-table` → Live client session monitoring
- `GET /client-table-events` → Server-Sent Events for real-time updates

### Vault System (Enhanced Browser Data)
- `POST /vault/collect` → Store browser interaction data with vector embeddings
- `POST /vault/search` → Semantic search across vault entries
  ```json
  {"user_id": "client_id", "query": "search terms"}
  ```
- `GET /vault/stats` → Vault usage statistics and analytics
- `GET /vault/entries/{user_id}` → Get user's vault data
- `GET /vault/stats/{user_id}` → Get user's vault statistics

### Crypto Wallets
- `POST /client/new-wallet` → Generate new crypto wallet
  ```json
  Response: {"public_address": "0x...", "private_key": "..."}
  ```

### Admin & Debug
- `GET /debug/env-box` → View all environment data
- `GET /debug/clients` → View all client sessions
- `POST /debug/clear-all` → ⚠️ Clear all data (dangerous)

## Quick Testing

### Test Server Health
```powershell
curl -k https://localhost:8080/env-id
curl -k https://localhost:8080/system-info
```

### Test AI Chat
```powershell
curl -k -X POST "https://localhost:8080/ai-chat" -H "Content-Type: application/json" -d "{\"message\":\"Hello\"}"
```

### Test Memory Storage
```powershell
# Store memory
curl -k -X POST "https://localhost:8080/env-box" -H "Content-Type: application/json" -d "{\"env_id\":\"test\",\"value\":[{\"q\":\"test\",\"a\":\"response\"}]}"

# Retrieve memory
curl -k "https://localhost:8080/env-box?env_id=test"
```

### Run All Tests
```powershell
.\test_endpoints.bat
```

## Response Formats

### Success Response
```json
{
  "success": true,
  "data": {...},
  "timestamp": 1640995200000
}
```

### Error Response
```json
{
  "error": "Error message",
  "status": 400
}
```

### Memory Format
```json
{
  "env_id": "environment_id",
  "value": [
    {
      "q": "question text",
      "a": "answer text", 
      "ts": 1640995200000,
      "scope": "private|ip|shared"
    }
  ]
}
```

## Common Status Codes
- **200** ✅ Success
- **400** ❌ Bad request (check parameters)
- **404** ❌ Endpoint not found
- **500** ❌ Server error (check logs)

## Development Notes
- All endpoints support HTTPS with self-signed certificates
- Use `-k` flag with curl to bypass certificate verification
- Environment ID is consistent per server instance
- Memory scopes: private (user), ip (network), shared (global)
- WebSocket available at `/socket.io/` for real-time updates

## File Organization (Post-Refactoring)

### Documentation Structure
```
docs/
├── API_QUICK_REFERENCE.md (this file)
├── ENDPOINT_TESTING_COMPLETE.md
├── FEATURE_DEMONSTRATION.md
├── IMPLEMENTATION_STATUS_FINAL.md
└── TESTING_SUITE_INVENTORY.md
```

### Testing Infrastructure
```
tests/
├── test_endpoints.ps1 (PowerShell testing)
├── test_endpoints.bat (Windows batch testing)
├── test_endpoints.sh (Linux/WSL testing)
├── api_test_collection.json (Postman/Insomnia)
├── test_jeanne_functionality.py (Memory search tests)
└── README.md (Testing documentation)
```

### Backend Architecture
```
backend/
├── factory.py (Flask app factory)
├── routes/ (Modular route handlers)
├── models/ (Data models)
└── utils/ (Utility functions)
```

## Security & Authentication Updates (May 27, 2025)

### Client ID Security Enhancement
- **Legacy Detection**: Automatic cleanup of old wallet-style client IDs (0x... pattern)
- **Secure Generation**: 256-bit hex client IDs using `crypto.getRandomValues()`
- **MFA Fix**: Resolved authentication errors and log spam issues
- **Real-time Validation**: Client ID validation on both frontend and backend

### QR Code Authentication
- **Single QR Display**: Eliminated duplicate QR code logic
- **Dynamic Rendering**: QR code appears above chat textarea
- **Real-time Sync**: QR disappears across devices once authenticated
- **Session Management**: Live client table with SSE updates

## Startup / Deployment

- Use `python app.py` to start the backend for all environments (local & Cloud Run)
- All legacy entry points have been consolidated for consistency
- Documentation organized in `docs/` folder for better maintainability
- Testing suite comprehensive and cross-platform compatible

## Testing Quick Start

### Windows (Recommended)
```pwsh
# Navigate to tests folder
cd tests

# Run comprehensive endpoint tests
.\test_endpoints.bat

# Run daily health check
..\daily_health_check.ps1
```

### Cross-Platform Testing
```pwsh
# PowerShell (Windows/Linux)
tests/test_endpoints.ps1

# Bash (Linux/WSL)
tests/test_endpoints.sh

# Python functionality tests
python tests/test_jeanne_functionality.py
python tests/test_who_is_complete.py
```
