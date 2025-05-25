# ICI Collaborative Memory Web App

A Flask-based collaborative memory web application supporting real-time, multi-user chat and memory sharing across browsers and devices.

## Features

- **Collaborative Chat & Memory**: Main chat page with three memory scopes:
  - **Shared Memory**: (env-id) - visible to all clients with the same environment hash.
  - **IP Shared Memory**: (env-id + public IP) - visible to all clients sharing the same environment and public IP.
  - **Private Memory**: (env-id + public IP + browser) - visible only to the current browser.
- **Real-Time Updates**: Shared memory updates are broadcast instantly to all connected clients using WebSockets (Flask-SocketIO + Socket.IO JS client).
- **QR Code Authentication**: Users authenticate by scanning a QR code, which links their session to a unique client ID.
- **Live Client Table**: `/join` page displays a live-updating table of all client sessions (using SSE for admin tools).
- **Recovery & Admin Tools**: `/recovery` page allows recovery of lost memory, client management, and deletion of client/session records.
- **Merge & Deduplication Logic**: Shared memory is a running total of all private chats, with deduplication by timestamp and question.
- **Markdown README Portal**: The landing page displays project info and navigation, rendering the latest README.md.
- **Modern, Accessible UI**: Semantic HTML, accessible forms, and responsive design.

## How It Works

- **Memory Model**: All chat messages are stored as arrays of objects (with `q`, `a`, `ts`, and optional `user` fields) in memory. Shared memory is keyed by environment hash (`env-id`).
- **Real-Time Sync**: When any client updates shared memory, a `shared_memory_updated` event is broadcast via WebSockets. All connected browsers instantly refresh their shared chat.
- **Private/Shared Merge**: If shared memory is lost, clients reshare their private memory to restore the shared state.
- **No Email Logic**: All references to email have been removed from backend, frontend, and templates.

## API Endpoints

### Main UI & Info
- `/` : Portal landing page with README and navigation.
- `/chat` : Main chat interface (shared, IP, and private memory boxes).
- `/readme` : Raw README.md as plain text.
- `/health` : Health check page.
- `/env-id` : Returns current environment ID as JSON.
- `/env-id-html` : Returns current environment ID as HTML.
- `/data` : Returns a random key (demo endpoint).

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
- **Flask-SocketIO** for WebSocket support
- **Socket.IO JS client** for real-time updates
- **Server-Sent Events (SSE)** for admin live tables
- **HTML5, CSS, JavaScript** (vanilla, no frameworks)

## Running Locally

1. Install dependencies:
   ```sh
   pip install flask flask-socketio eventlet
   ```
2. Run the app:
   ```sh
   python app.py
   ```
3. Open [http://localhost:8080](http://localhost:8080) in your browser.

## Notes

- All memory is in-memory only (demo mode). For production, use persistent storage.
- Real-time chat requires WebSocket support (Flask-SocketIO + eventlet or gevent).
- No user emails or passwords are stored or required.

## Policies, Terms, and Governance

The ICI Collaborative Memory Web App includes a dedicated area for policies, terms, and governance documentation to help users and organizations comply with legal and privacy requirements.

- **Cookie Consent**: A cookie consent banner is shown to all users on first visit. Consent is required for session management and analytics cookies. See the [Policies page](/policies) for details.
- **Policies Page**: Visit [/policies](/policies) for full documentation of:
  - Cookie Policy
  - Terms of Use
  - Data Governance
  - Contact information

**Links:**
- [Cookie Policy and Terms](/policies)

This area is designed to be easily extensible for additional compliance, privacy, or governance requirements.

---

Open source. Contributions welcome!
