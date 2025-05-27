# ICI Chat Testing Suite

This folder contains all testing files for the ICI Chat application. All test files have been organized here following the **Single Entry Point Rule** - only one `app.py` exists in the root directory.

## 📁 Current Test Files

### Core Test Suites
- **`test_endpoints.ps1`** - PowerShell script for comprehensive endpoint testing
- **`test_endpoints.bat`** - Windows batch file for endpoint testing (recommended for Windows)
- **`test_endpoints.sh`** - Bash script for Linux/WSL endpoint testing
- **`api_test_collection.json`** - API collection for Postman/Insomnia tools

### Functionality Tests
- **`test_jeanne_functionality.py`** - Tests "Who is [person]?" search functionality
- **`test_who_is_complete.py`** - Tests cross-memory search capabilities

### Documentation
- **`TESTING_SUITE_INVENTORY.md`** - Complete inventory of testing infrastructure
- **`ENDPOINT_TESTING_COMPLETE.md`** - Endpoint testing completion documentation

## 🎯 Current Endpoints Tested

Based on the current application architecture (as of May 2025), these test suites cover:

### Core System
- `GET /env-id` → Environment identifier
- `GET /system-info` → Server status and Python info
- `GET /health` → Health check with live data stream

### Main Application Pages
- `GET /` → Landing page
- `GET /chat` → AI chat interface
- `GET /join` → QR authentication and client table
- `GET /admin` → Admin dashboard
- `GET /learn` → Learning guide
- `GET /readme` → Project documentation
- `GET /policies` → Policies and terms

### API Endpoints
- `POST /ai-chat` → Basic AI conversation
- `POST /ai-chat-enhanced` → AI chat with file uploads
- `GET /env-box` → Get shared memory
- `POST /env-box` → Store shared memory
- `GET /ip-box` → Get IP-shared memory
- `POST /ip-box` → Store IP-shared memory
- `POST /client-register` → Register new client
- `GET /clients` → List all registered clients
- `POST /client-heartbeat` → Update client status
- `POST /vault/collect` → Store browser data
- `POST /vault/search` → Search vault entries

### Debug Endpoints
- `GET /debug/env-box` → Debug environment data
- `GET /debug/ip-box` → Debug IP data
- `GET /debug/clients` → Debug client data

## 🧹 Cleanup Summary

Removed outdated test files that were testing non-existent endpoints or old functionality:
- `test_alice_data.json` - Old test data
- `test_restart_fix.html` - Specific old bug test
- `test_results_final.md` - Old test results
- `test_vault_data.json`, `test_vault.json` - Outdated vault test data
- `test_payload.json` - Generic test payload
- `test_endpoint_fixes.ps1` - Duplicate test script
- `test_endpoints_win.ps1` - Duplicate test script
- `test_memory_system.ps1` - Old memory system tests
- `test_who_is_functionality.ps1` - Duplicate of Python version

## 🚀 Running Tests

### Quick Test (Recommended)
```bash
# Windows
tests\test_endpoints.bat

# PowerShell
tests\test_endpoints.ps1

# Linux/WSL
tests/test_endpoints.sh
```

### Functionality Tests
```bash
# Test person search functionality
python tests/test_jeanne_functionality.py
python tests/test_who_is_complete.py
```

All tests are designed to work with the current modular backend architecture where `backend/factory.py` contains the Flask application factory and `app.py` serves as the single entry point.
