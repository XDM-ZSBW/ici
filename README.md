# ICI: Your AI Memory Companion for Enhanced Independence

An open-source, AI-powered memory assistant designed with and for individuals with cognitive disabilities. ICI provides ethical, privacy-respecting memory support through collaborative, adaptive technology that enhances independence and well-being.

---

## 🎯 Solution Architecture Skills

> **Key competencies demonstrated in building this AI-powered accessibility solution:**

### 💡 **Human-Centered AI Design & Accessibility Engineering**
Expertise in designing AI systems with progressive confirmation methodologies, multi-modal explanations, and "unapologetically naggy" safety mechanisms that prioritize user agency and cognitive accessibility over convenience.

### 🛡️ **Collaborative Memory Architecture & Privacy Engineering** 
Advanced skills in architecting multi-scope data sharing systems (private/IP/shared) with real-time synchronization, QR-based authentication, and privacy-first design principles for sensitive user populations.

### 🚀 **Full-Stack AI Solution Architecture**
Proven ability to design and implement complete AI-powered applications including Flask/SocketIO backends, responsive frontends, vector databases, memory systems, and cloud deployment strategies with progressive startup methodologies.

---

## Mission & Vision

**Purpose**: ICI is an open-source AI memory companion designed with and for individuals with cognitive disabilities, providing ethical, privacy-respecting memory support.

**Mission**: To enhance independence and well-being through AI-powered, personalized memory assistance that empowers rather than replaces human agency.

**Vision**: A world where cognitive support technology is accessible, dignified, and designed by the communities it serves.

## Core Features

- **AI-Powered Memory Support**: Intelligent reminders, prompts, and memory organization tailored to individual needs and preferences.
- **Collaborative Memory Sharing**: Three memory scopes with user control:
  - **Private Memory**: Personal, secure storage for individual use
  - **IP Shared Memory**: Shared with trusted devices on the same network
  - **Shared Memory**: Community memory for broader collaboration
- **Real-Time Synchronization**: ~~Instant updates across devices using WebSockets for seamless memory access.~~
- **QR Code Authentication**: Simple, accessible authentication system for easy device linking.
- **Adaptive Interface**: UI that learns and adapts to user preferences and accessibility needs.
- **Privacy-First Design**: User-controlled data sharing with transparent privacy policies.
- **Progressive Confirmation System**: "Unapologetically naggy" confirmation methodology that ensures user understanding and safety through multiple explanation methods and accessible confirmations.
- **Modular Architecture**: Clean, maintainable codebase supporting ongoing development and customization.

## Design Philosophy

### Progressive Confirmation & Accessibility
ICI implements an intentionally thorough confirmation system that prioritizes user safety and understanding over convenience. This "unapologetically naggy" approach includes:

- **Multi-Modal Explanations**: Actions are explained through various methods (visual, textual, interactive) to accommodate different learning styles and accessibility needs
- **Progressive Detail**: Information is presented with increasing detail and context to ensure comprehensive understanding
- **Graceful Repetition**: The system will ask for confirmation multiple times in different ways, particularly for significant actions
- **Accessibility-First Design**: All confirmations work seamlessly with screen readers, keyboard navigation, and assistive technologies
- **User Agency**: Maintains user control and informed consent throughout all interactions

This methodology ensures that individuals with cognitive disabilities maintain full autonomy while receiving appropriate support and protection.

## Architecture

ICI uses a modern, modular architecture designed for maintainability and extensibility:

### Backend Structure
- **`backend/`**: Main Flask application package
  - **`factory.py`**: Flask app factory with blueprint registration
  - **`routes/`**: Modular route handlers
    - `chat.py` & `chat_new.py`: Chat and memory management routes
    - `client.py`: Client session management routes  
    - `admin.py`: Administrative and recovery tools
    - `memory.py`: Memory storage and retrieval endpoints
    - `vault.py` & `vault_new.py`: Data vault and search functionality
    - `learn.py`: Learning guide and documentation routes
  - **`models/`**: Data models and schema definitions
    - `memory.py`: Memory storage models
    - `vault.py`: Vault data models
  - **`utils/`**: Utility functions and helpers
    - `id_utils.py`: ID generation and validation utilities
    - `memory_utils.py`: Memory search and retrieval utilities

### Frontend Structure
- **Modular JavaScript**: Split from monolithic to focused modules in `static/`
  - `app.js`: Main application orchestration
  - `memory.js`: Memory management and display logic
  - `ui.js`: User interface interactions
  - `api.js`: Backend communication utilities
  - `auth.js`: Authentication management
  - `debug.js`: Debug tools and system testing
  - `chat.js`: Main chat interface functionality
  - `client.js` & `client-table.js`: Client management interfaces
  - `join.js`: Authentication and joining functionality

### Templates
- **Accessible HTML**: Semantic, screen-reader friendly templates in `templates/`
- **Responsive Design**: Mobile-first, adaptive layouts
- **Component System**: Reusable header/footer components (`_header.html`, `_footer.html`)

### Documentation & Testing
- **`docs/`**: Technical documentation and API references
  - API quick reference, feature demonstrations, implementation status
- **`tests/`**: Comprehensive testing suite
  - Endpoint testing scripts for multiple platforms
  - Functionality tests and API collections

## How Memory Support Works

- **Personalized AI**: The system learns individual patterns and preferences to provide increasingly tailored support.
- **Collaborative Design**: Built with the cognitive disability community as equal partners in development.
- **Ethical Foundation**: Every feature prioritizes dignity, autonomy, and user agency.
- **Real-Time Sync**: Memory updates synchronize instantly across devices for consistent access.
- **Privacy Control**: Users maintain complete control over what information is shared and with whom.

## API Endpoints

### Main UI & Info
- `/` : Portal landing page with README and navigation
- `/chat` : Main chat interface with secure client ID generation and QR authentication
- `/client` : Client authenticated chat interface with wallet integration
- `/admin` : Administrative dashboard with system statistics
- `/join` : QR code authentication and live client session management
- `/roadmap` : Project roadmap and Gantt chart
- `/policies` : Privacy policies and terms of service
- `/readme` : Rendered README documentation
- `/learn` : Learning guide for collaborative memory usage
- `/health` : Comprehensive health check with live system status
- `/changelog` : Version history and update documentation

### Enhanced Memory APIs
- `/env-box` : Shared memory API with cross-environment search
  - **GET**: `?env_id=<id>` — Returns memory data for environment
  - **POST**: Stores/merges shared memory with timestamp tracking
- `/ip-box` : IP-shared memory API with network-scoped storage
  - **GET**: `?env_id=<id>&public_ip=<ip>` — Returns IP-scoped memory
  - **POST**: Stores IP-specific shared memory
- `/env-box-aggregate` : Cross-environment memory aggregation and search

### Advanced AI Chat
- `/ai-chat` : Enhanced AI conversation with memory integration
- `/ai-chat-enhanced` : AI chat with file upload and screenshot support
- `/ask` : Legacy AI endpoint (maintained for compatibility)

### Secure Client Management
- `/client-register` : Secure client registration with 256-bit hex IDs
- `/client-heartbeat` : Client keepalive and session management
- `/client-table` : Live client session monitoring
- `/client-table-events` : Real-time SSE updates for client status
- `/clients` : Client listing and management APIs

### Vault System (Browser Data Collection)
- `/vault/collect` : Store browser interaction data with vector embeddings
- `/vault/search` : Advanced semantic search across vault entries
- `/vault/stats` : Vault usage statistics and analytics

### Admin & Recovery Tools
- `/recovery` : Administrative recovery and system management tools
- `/debug/*` : Comprehensive debugging endpoints for system diagnostics
- `/system-info` : Detailed system information and Python environment data

## Technologies Used

### Backend
- **Flask** (Python 3.9+) with modular blueprint architecture
- **SocketIO** for real-time client synchronization
- **Vector embeddings** for semantic search capabilities
- **SQLite** for lightweight data persistence
- **SSL/TLS** with auto-generated certificates for development

### Frontend
- **Vanilla JavaScript** (ES6+) with modular design
- **HTML5** with semantic, accessible markup
- **CSS3** with responsive, mobile-first design
- **WebSocket** for real-time communication
- **Crypto API** for secure 256-bit client ID generation

### Security & Authentication
- **256-bit hex client IDs** replacing legacy wallet-style identifiers
- **QR code authentication** for device linking
- **HTTPS enforcement** for all communications
- **Multi-factor authentication** with progressive confirmation

### Development & Deployment
- **Docker** containerization for consistent deployment
- **Google Cloud Run** optimized architecture
- **Comprehensive testing suite** with multiple platform support
- **Auto-reload development server** with debug mode

## 🚀 Running the Application

**Use `app.py` as the ONLY entry point for all environments (local & Cloud Run):**

```pwsh
python app.py
```

### Local Development Features
- **Auto-SSL**: HTTPS certificates auto-generated if missing using OpenSSL
- **Hot Reload**: Flask debug mode enabled for automatic code reloading
- **Secure Client IDs**: Automatic detection and cleanup of legacy wallet-style IDs
- **Comprehensive Logging**: Detailed logs for debugging MFA and authentication issues
- **Real-time Sync**: WebSocket-based real-time updates across all connected clients

### Cloud Run Deployment
- **Optimized Architecture**: Lightweight design for fast cold starts
- **SSL Termination**: Cloud Run handles HTTPS termination automatically
- **Container Ready**: Docker configuration optimized for serverless deployment
- **Environment Variables**: Secure configuration management for production

### Development Setup
1. **Install Python 3.9+** and pip
2. **Install OpenSSL** (required for local HTTPS)
   - [Download OpenSSL for Windows](https://slproweb.com/products/Win32OpenSSL.html)
   - Add OpenSSL `bin` directory to your PATH
3. **Install dependencies**
   ```pwsh
   pip install -r requirements.txt
   ```
4. **Run the application**
   ```pwsh
   python app.py
   ```
   - Visit: https://localhost:8080
   - Auto-generated certificates stored as `cert.pem` and `key.pem`

> **Note:**
> All legacy entry points have been deprecated. The refactored architecture uses only `app.py` for consistency across all deployment environments. Documentation and testing infrastructure have been organized into `docs/` and `tests/` folders respectively.

## Community & Ethics

ICI is developed **with** and **for** the cognitive disability community, not simply for them. We believe in:

- **Nothing About Us, Without Us**: Equal partnership in design and development
- **Dignity & Autonomy**: Technology that enhances rather than replaces human agency  
- **Accessibility First**: Universal design principles from the ground up
- **Open Source Transparency**: All code, decisions, and governance are transparent
- **Privacy as a Right**: User data control and ethical AI practices

### Get Involved
- **Contributors Welcome**: Join our development community
- **Feedback Valued**: Share your experiences and suggestions
- **Partnership Opportunities**: Organizations supporting cognitive accessibility
- **Research Collaboration**: Academic institutions studying assistive technology

## Privacy, Ethics & Governance

ICI operates under strict ethical guidelines developed in partnership with disability rights advocates:

- **Informed Consent**: Clear, accessible explanations of all data practices
- **Data Minimization**: Only collect information necessary for memory support
- **User Control**: Complete control over data sharing and retention
- **Algorithmic Transparency**: Open source AI decision-making processes
- **Community Governance**: User community involvement in policy decisions

### Documentation
- **[Policies & Terms](/policies)**: Complete privacy and usage policies
- **Cookie Consent**: Transparent cookie usage with user control
- **Data Governance**: Community-driven data protection standards
- **Ethical AI**: Guidelines for responsible cognitive support technology

### Contact & Support
- **Community**: Join our inclusive development community
- **Support**: Accessible help and documentation
- **Feedback**: Multiple ways to share experiences and suggestions
- **Advocacy**: Partnership with disability rights organizations

---

**ICI: Technology that respects, empowers, and serves the cognitive disability community with dignity and partnership.**

*Open source. Community-driven. Ethically-focused. Contributions and partnerships welcome.*

# ICI Chat - Modern AI Chat & Memory Platform

## Features
- AI chat with local LLM (DistilGPT2) and live system prompt tuning
- Secure local development with automated HTTPS (self-signed certs)
- Memory and screenshot support (requires HTTPS)
- Crypto wallet generation and admin tools
- Modular backend (Flask only)
- Ready for Google Cloud Run deployment

## Quick Start (Local Dev)

1. **Install Python 3.9+ and pip**
2. **Install OpenSSL**
   - [Download OpenSSL for Windows](https://slproweb.com/products/Win32OpenSSL.html)
   - Add the OpenSSL `bin` directory to your PATH
3. **Install dependencies**
   ```pwsh
   pip install -r requirements.txt
   ```
4. **Run the server**
   ```pwsh
   python app.py
   ```
   - The server will auto-generate `cert.pem` and `key.pem` for HTTPS if missing.
   - Visit: https://localhost:8080

## Google Cloud Run Deployment
- Use the provided `Dockerfile` for containerization.
- Cloud Run provides HTTPS by default—no extra SSL config needed.
- For persistent memory, use Google Cloud Storage or Firestore.
- Ensure all environment variables and secrets are set in Cloud Run.

## Lessons Learned / Nuggets

### SSL & HTTPS for Local Dev
- Many browser APIs (like screenshot capture) require HTTPS, even for localhost.
- Use Flask's SSL support with self-signed certs for local testing.
- Automate cert generation with OpenSSL in your launcher script.
- If OpenSSL is missing, fail fast and print a clear error.

### OpenSSL on Windows
- Download from [slproweb.com](https://slproweb.com/products/Win32OpenSSL.html)
- Add the `bin` directory to your PATH so Python can find `openssl.exe`.

### Cloud Run Deployment
- **Lightweight Architecture**: Optimized for Google Cloud Run with 1 CPU and 512MB RAM
- Use a `Dockerfile` based on `python:3.9-slim` for minimal footprint
- Expose port 8080 and use HTTPS (Cloud Run handles certs)
- **No Heavy Dependencies**: Removed transformers, torch, and vector databases for faster builds
- **Fast Cold Starts**: Lightweight implementation eliminates model loading delays

### AI Chat & Memory
- **Text-Based Search**: Uses efficient string matching instead of vector embeddings
- **Memory System**: Lightweight in-memory storage with simple text-based retrieval
- Store user memories and include them in the prompt for context
- For screenshots, use OCR to extract text and store as memory
- **Cloud Run Ready**: Optimized for serverless deployment constraints

### Admin & Wallets
- Admin UI allows wallet creation and management.
- Use `/client/new-wallet` endpoint for new crypto addresses.

---

# ICI Chat API & Web Endpoints

Below is a complete list of all available endpoints, their purpose, and usage. Endpoints marked with [HTML] return a web page; others return JSON or other formats.

## Main Endpoints

- `/` [HTML] — Home page
- `/chat` [HTML] — Chat interface (guest or client)
- `/client` [HTML] — Client authenticated chat (shows wallet address, QR, etc.)
- `/roadmap` [HTML] — Project roadmap and Gantt chart
- `/policies` [HTML] — Policies and terms
- `/readme` [HTML] — Rendered README documentation
- `/health` [HTML] — Health check/status page
- `/recovery` [HTML] — Admin/Recovery tools

## API Endpoints

- `/ai-chat` — POST: Chat as guest (uses env-id for memory)
- `/ai-chat-enhanced` — POST: Chat with file/screenshot support
- `/client-register` — POST: Register a client (returns wallet address)
- `/client-heartbeat` — POST: Client keepalive
- `/clients` — List all registered clients
- `/client/<client_id>/data` — Get client data
- `/client/<client_id>/remove` — Remove client
- `/debug/env-box` — Admin: view all env-box data
- `/debug/ip-box` — Admin: view all IP-box data
- `/debug/clients` — Admin: view all client data
- `/debug/clear-all` — Admin: clear all data

## Auth & QR Code

- When a user scans a QR code on the chat page, the QR disappears and the UI updates to show client details (from client.html). The user's wallet address is now used as the unique identifier for all memory and chat operations, instead of the previous guest env-id. Memory continuity is preserved.

## Enhanced Authentication & Security Features

### Secure Client ID System
- **256-bit Hex Client IDs**: Cryptographically secure client identification
- **Legacy ID Detection**: Automatic detection and cleanup of old wallet-style IDs (0x... pattern)
- **Secure Generation**: Uses `crypto.getRandomValues()` for entropy
- **MFA Integration**: Resolves authentication errors and log spam

### QR Code Authentication (Updated May 27, 2025)
- **Dynamic QR Display**: QR code appears above the "Ask AI" textarea on the chat page
- **Real-time Synchronization**: QR code disappears across all tabs/devices once authenticated
- **Session Management**: Live client session table with real-time updates
- **Device Linking**: Seamless device authentication and memory continuity
- **No Duplicate QR Codes**: Eliminated legacy QR code logic for clean user experience

### Progressive Confirmation System
The "unapologetically naggy" confirmation methodology ensures user safety:
- **Multi-Modal Explanations**: Visual, textual, and interactive confirmations
- **Accessibility Integration**: Screen reader compatibility and keyboard navigation
- **Graceful Repetition**: Multiple confirmation methods for important actions
- **User Agency**: Maintains informed consent throughout all interactions

---

For more details, see the web UI or contact the project maintainers.

## Learn Endpoint
See `/learn` for a live Markdown knowledge base of lessons learned, deployment tips, and dev workflow nuggets.
