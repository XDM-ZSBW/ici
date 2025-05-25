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

## Endpoints

- `/` - Portal landing page with README and navigation.
- `/chat` - Main chat interface (shared, IP, and private memory boxes).
- `/env-box` - Shared memory API (GET/POST, array of messages).
- `/client-box` - IP shared memory API (GET/POST).
- `/join` - QR code for authentication and live client/session table.
- `/client/<id>` - Client details as JSON, always creates a record if missing.
- `/recovery` - Admin tools for memory recovery and client management.
- `/client-table` - JSON table of all client sessions.
- `/client-table-events` - SSE for live client table updates.
- `/delete-client-row`, `/delete-all-client-rows` - Admin endpoints for client/session deletion.

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

---

Open source. Contributions welcome!
