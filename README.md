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
  - **`app.py`**: Flask app factory with blueprint registration
  - **`routes/`**: Modular route handlers
    - `chat.py`: Chat and memory management routes
    - `client.py`: Client session management routes  
    - `admin.py`: Administrative and recovery tools
  - **`models/`**: Data models and schema definitions
  - **`utils/`**: Utility functions and helpers

### Frontend Structure
- **Modular JavaScript**: Split from monolithic to focused modules
  - `app.js`: Main application orchestration
  - `memory.js`: Memory management and display logic
  - `ui.js`: User interface interactions
  - `api.js`: Backend communication utilities
  - `auth.js`: Authentication management
  - `debug.js`: Debug tools and system testing

### Templates
- **Accessible HTML**: Semantic, screen-reader friendly templates
- **Responsive Design**: Mobile-first, adaptive layouts
- **Component System**: Reusable header/footer components

## How Memory Support Works

- **Personalized AI**: The system learns individual patterns and preferences to provide increasingly tailored support.
- **Collaborative Design**: Built with the cognitive disability community as equal partners in development.
- **Ethical Foundation**: Every feature prioritizes dignity, autonomy, and user agency.
- **Real-Time Sync**: Memory updates synchronize instantly across devices for consistent access.
- **Privacy Control**: Users maintain complete control over what information is shared and with whom.

## API Endpoints

### Main UI & Info
- `/` : Portal landing page with README and navigation.
- `/chat` : Main chat interface (shared, IP, and private memory boxes).
- `/client` : Client authenticated chat (shows wallet address, QR, etc.)
- `/roadmap` : Project roadmap and Gantt chart
- `/policies` : Policies and terms
- `/readme` : Rendered README documentation
- `/health` : Health check/status page.
- `/recovery` : Admin/Recovery tools

### Memory APIs
- `/env-box` : Shared memory API (GET/POST)
  - **GET**: `?env_id=<id>` — Returns `{ "value": [ ...messages... ] }` for the given env-id.
  - **POST**: `{ "env_id": <id>, "value": [ ...messages... ] }` — Sets/merges shared memory for env-id.
- `/client-box` : IP-shared memory API (GET/POST)
  - **GET**: `?env_id=<id>&public_ip=<ip>` — Returns `{ "value": [ ...messages... ] }` for the given env-id and IP.
  - **POST**: `{ "env_id": <id>, "public_ip": <ip>, "value": [ ...messages... ] }` — Sets/merges IP-shared memory.
- `/env-box-aggregate` : Returns all shared memory across all env-ids, deduplicated and sorted.

### Chat & AI
- `/ask` : POST `{ "question": <str>, "user_id": <str> }` — Returns `{ "answer": <str> }` (demo AI echo).

### Client & Session Management
- `/join` : QR code for authentication and live client/session table.
- `/join/<client_id>` : Placeholder for joining with a specific client ID.
- `/client/<id>` : Client details page (creates record if missing).
- `/client-remember` : POST `{ "client_id": <str> }` — Updates or creates a client record.
- `/client-lookup` : POST `{ "client_id": <str> }` — Looks up a client record.
- `/client-table` : Returns JSON array of all client sessions.
- `/client-table-events` : Server-Sent Events (SSE) for live client table updates.
- `/client-table-restore` : POST — Restore client table from JSON array.

### Admin & Recovery
- `/recovery` : Admin tools for memory recovery and client management.
- `/delete-client-row` : POST `{ "client_id": <str>, "private_id": <str> }` — Deletes a specific client/session row.
- `/delete-all-client-rows` : POST — Deletes all client/session rows for current env-id.
- `/file-lost-memory-report` : POST `{ "env_id": <str>, "details": <str> }` — File a lost memory report.
- `/get-lost-memory-reports` : GET `?env_id=<id>` — Get all lost memory reports for env-id.

## Technologies Used

- **Flask** (Python)
- **HTML5, CSS, JavaScript** (vanilla, no frameworks)

## 🚀 Running the Application

**Use `app.py` as the ONLY entry point for all environments (local & Cloud Run):**

```sh
python app.py
```

- For local development, HTTPS is auto-configured if certs are present.
- For Cloud Run, simply deploy with `app.py` as the entrypoint (Cloud Run handles SSL termination).

> **Note:**
> `run_refactored.py` is deprecated and should NOT be used. It is retained for reference only and will be removed in a future release. All startup and deployment should use `app.py`.

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

## QR Code Authentication Flow

When a user scans the QR code on the chat page:
- The QR code UI disappears.
- The client details UI (from client.html) is shown in its place.
- All chat and memory operations now use the wallet address as the unique identifier (user_id), instead of the previous guest env-id.
- Memory continuity is preserved: the user's previous chat history and facts remain accessible, now associated with their wallet address.

---

For more details, see the web UI or contact the project maintainers.

## Learn Endpoint
See `/learn` for a live Markdown knowledge base of lessons learned, deployment tips, and dev workflow nuggets.
