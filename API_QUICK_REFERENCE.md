# 🚀 ICI Chat API Quick Reference

## Essential Endpoints

### Core System
- `GET /env-id` → Get environment identifier
- `GET /system-info` → Server status and Python info
- `GET /health` → Health check with live data stream

### Main Application
- `GET /` → Landing page
- `GET /chat` → AI chat interface
- `GET /join` → QR authentication and client table
- `GET /admin` → Admin dashboard
- `GET /learn` → Learning guide for safe collaborative memory usage
- `GET /readme` → Project README documentation
- `GET /changelog` → Version history and updates

### AI Chat
- `POST /ai-chat` → Basic AI conversation
  ```json
  {"message": "Hello", "system_prompt": "You are helpful"}
  ```
- `POST /ai-chat-enhanced` → AI chat with file uploads
  ```json
  {"message": "Analyze this", "files": [...], "system_prompt": "..."}
  ```

### Memory System
- `GET /env-box?env_id=xxx` → Get shared memory
- `POST /env-box` → Store shared memory
  ```json
  {"env_id": "xxx", "value": [{"q": "question", "a": "answer", "ts": 123}]}
  ```
- `GET /ip-box?env_id=xxx&public_ip=yyy` → Get IP-shared memory
- `POST /ip-box` → Store IP-shared memory

### Client Management
- `POST /client-register` → Register new client
  ```json
  {"client_id": "xxx", "env_id": "yyy", "public_ip": "zzz"}
  ```
- `GET /clients` → List all registered clients
- `POST /client-heartbeat` → Update client last-seen

### Vault (Browser Data)
- `POST /vault/collect` → Store browser interaction data
- `POST /vault/search` → Search vault entries
  ```json
  {"user_id": "xxx", "query": "search terms"}
  ```
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

## Startup / Entrypoint

- Use <code>python app.py</code> to start the backend for all environments (local & Cloud Run).
- <code>run_refactored.py</code> is deprecated and should not be used.
