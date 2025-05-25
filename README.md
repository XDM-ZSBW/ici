# ici

## Overview

This is a Python Flask web application prototype designed for Google Cloud Run deployment with continuous deployment capabilities. The app demonstrates advanced client-server synchronization with three different scopes of data sharing through interactive textboxes.

**Key Features:**
- **Three-tier data synchronization**: Global (env-id), IP-based (env-id + public IP), and private (browser-specific)
- **Offline-first architecture**: Changes persist during server downtime and sync when reconnected
- **Server restart recovery**: Automatic restoration of data from localStorage after server restarts
- **Cross-tab synchronization**: Real-time updates across browser tabs
- **Build versioning**: Automatic version generation based on code changes

## Core Functionality

### Interactive Textboxes
The main page (`/`) features three textboxes with different sharing scopes:

1. **Top Textbox (Global Scope)**
   - Shared across all clients with the same environment ID (env-id)
   - Server-synchronized with real-time updates
   - Auto-saves on input with 400ms debounce

2. **Middle Textbox (IP Scope)** 
   - Shared across all clients with the same env-id AND public IP address
   - Server-synchronized with real-time updates
   - Auto-saves on input with 400ms debounce

3. **Bottom Textbox (Private Scope)**
   - Private to the specific browser (client-id) within the same env-id and public IP
   - Stored in localStorage with cross-tab synchronization
   - Auto-saves on input with 400ms debounce

### Offline Behavior
- **Graceful degradation**: Top and middle textboxes disable when server is offline
- **Change preservation**: All offline changes are queued and merged when server reconnects
- **Visual feedback**: Offline textboxes are styled with red background
- **Data integrity**: No data loss during temporary network issues or server downtime

### Server Restart Recovery
- **Automatic detection**: Client detects when server storage has been cleared
- **Instant restoration**: Previous textbox values are immediately restored from localStorage
- **Server repopulation**: Restored values are pushed back to the server automatically
- **Edit protection**: Post-restoration editing is protected from polling overwrites for 15 seconds
- **User-driven reset**: Protection flags clear immediately when user starts typing
- **Console logging**: Restoration process is logged for debugging

## Collaborative Memory & Client Management

This app supports collaborative memory and client management for shared environments. It features:
- **Join via QR code**: `/join` page generates a QR code for easy device onboarding.
- **Client info page**: `/client/<private-id>` page for entering and updating email, with explicit save logic.
- **In-memory client table**: Tracks all client sessions, emails, IDs, timestamps, and history.
- **Live-updating tables**: `/join` and `/recovery` pages show real-time client tables using Server-Sent Events (SSE).
- **Recovery & admin tools**: `/recovery` page for reporting lost memory, viewing, and deleting client records (individually or all at once).
- **Robust offline/merge logic**: All memory is restored after server restarts using localStorage backup and auto-repopulation.

### Client Table Fields
- `email`: Client's email address (set on explicit save only, must be valid)
- `client_id`: Unique client identifier
- `timestamp`: Last update time
- `env_id`: Environment ID
- `env_id_elements`: Details used to generate env_id
- `private_id`: Private identifier for the client
- `private_id_elements`: Details used to generate private_id
- `previous_email`, `previous_client_id`: History of previous values

### QR Code Join Flow
- Visit `/join` to generate a QR code for the `/client/<private-id>` page.
- Scan the QR code to open the client info page on another device.
- Enter a valid email and save to create/update a client record.

### Live-updating Client Table (SSE)
- `/client-table-events` provides real-time updates to the client table using SSE (no polling).
- Both `/join` and `/recovery` pages display the table and update instantly on changes.

### Recovery & Admin Features
- `/recovery` page allows users to file a lost memory report and view all current clients for the environment.
- Each row has a delete button; a "Delete All" button removes all client records (no confirmation required).
- All deletions and updates are reflected live via SSE.

### Memory Restoration
- If the server restarts and loses in-memory data, clients automatically restore their memory from localStorage backup.
- Restoration is triggered on both `/join` and `/client/<id>` pages.

## Endpoints

## API Endpoints

- **GET /**  
  Returns the main application page with three interactive textboxes and build version display.

- **GET /health**  
  Returns the health check page for monitoring and load balancer health checks.

- **GET /data**  
  Returns a JSON object containing a randomly generated 256-bit key:
  ```json
  {
    "key": "aabbccddeeff00112233445566778899aabbccddeeff00112233445566778899"
  }
  ```

- **GET /env-id**  
  Redirects to the main page (`/`) - maintains compatibility with previous versions.

- **GET /env-id-html**  
  Returns a simplified page displaying environment ID, client ID, and a reset button.

- **GET/POST /env-box**  
  API for the global textbox (shared by env-id).
  - GET: Returns current value as JSON: `{"value": "content"}`
  - POST: Accepts JSON: `{"value": "new content"}` and returns `{"status": "ok"}`

- **GET/POST /client-box**  
  API for the IP-scoped textbox (shared by env-id + public IP).
  - GET: Requires `env_id` and `public_ip` query parameters
  - POST: Accepts JSON: `{"env_id": "...", "public_ip": "...", "value": "content"}`

- **GET /join**
  - Returns the join page with a QR code for `/client/<private-id>` and a live-updating client table.

- **GET /join/<client_id>**
  - Returns the join page for a specific client.

- **GET /client/<private-id>**
  - Returns the client info page for entering/updating email. Only valid emails are accepted, and records are created/updated on explicit save.

- **POST /client-remember**
  - Creates or updates a client record. Requires valid email and private-id.

- **GET /client-table**
  - Returns the full in-memory client table as JSON.

- **POST /client-table-restore**
  - Accepts a client-side backup of the client table and restores it on the server.

- **GET /client-table-events**
  - Server-Sent Events endpoint for live client table updates.

- **GET /recovery**
  - Returns the recovery page with a lost memory report form and live client table.

- **POST /delete-client-row**
  - Deletes a single client record by private-id.

- **POST /delete-all-client-rows**
  - Deletes all client records for the current environment.

## Technical Implementation

### Environment ID Generation
The `env-id` is generated from a hash of:
- Python executable path
- Python version
- Platform information
- Python implementation

This creates a unique identifier per environment while remaining consistent across app restarts.

### Build Version System
- **Automatic versioning**: Generated from SHA1 hash of app.py content + modification time
- **10-character limit**: Truncated to first 10 alphanumeric characters
- **Cached globally**: Version calculated once per server instance
- **Visible in UI**: Displayed in the page header for deployment tracking

### Client ID Generation
- **Browser-specific**: Generated from env-id + public IP + user agent
- **Base64 encoded**: 16-character identifier for localStorage keys
- **Persistent**: Remains consistent within the same browser/environment

### Data Persistence Strategy
- **Server storage**: In-memory dictionaries (production should use persistent storage)
- **Client storage**: localStorage with structured JSON for all textbox states
- **Conflict resolution**: Client changes take precedence, server handles merging
- **Cross-tab sync**: Storage events synchronize private textbox across browser tabs

### Post-Restart Editing Protection
- **Restoration flags**: `envBoxJustRestored` and `clientBoxJustRestored` prevent polling overwrites
- **Time-based protection**: 15-second automatic reset of protection flags
- **User-driven reset**: Flags clear immediately when user starts typing
- **Dual protection**: Works alongside the existing 10-second user change protection
- **Race condition prevention**: Prevents polling from overriding restored values during the critical restoration period

## Local Development

To run the app locally:

```bash
python app.py
```

The server will start on port 8080 by default.  
You can access it at [http://localhost:8080](http://localhost:8080).

## Docker Build Testing

To build and run the Docker image locally:

```bash
docker build -t my-app .
docker run -p 8080:8080 my-app
```

## Build and Deployment (Google Cloud Run)

To build and deploy this application to Google Cloud Run, use the following command (ensure you have a GCS bucket for logs):

```bash
gcloud builds submit --config cloudbuild.yaml \
  --substitutions=_CACHE_BUST=$(date +%s),_SERVICE_NAME="your-service-name",_PLATFORM="managed",_REGION="your-region" \
  --gcs-log-dir=gs://your-log-bucket/logs .
```

- Replace the substitutions with your service name, region, and log bucket as needed.
- See [Creating a Cloud Storage bucket](https://cloud.google.com/storage/docs/creating-buckets) for instructions.

## Changelog

### [2025-05-25] - Collaborative Memory & Recovery Features
- **Collaborative memory system**: In-memory client table with full history, explicit email save, and robust merge logic
- **Join page with QR code**: Easy onboarding for new devices, live-updating client table (SSE)
- **Client info page**: Email entry, explicit save, and history tracking
- **Recovery page**: Lost memory reporting, live client table, and admin delete tools
- **SSE for live updates**: No polling required for join/recovery tables
- **Memory restoration**: Automatic repopulation from localStorage after server restart
- **UI/UX improvements**: Clickable client URLs, delete buttons, and improved feedback

### [2025-05-24] - Current Prototype
- **Complete textbox system implementation**: Three textboxes with different sharing scopes
- **Advanced offline handling**: Queue-based change tracking with merge logic on reconnection
- **Server restart recovery**: Automatic detection and restoration of previous values
- **Cross-tab synchronization**: Real-time updates for private textbox across browser tabs
- **Performance optimization**: Increased polling intervals to 5 seconds, 10-second user change protection
- **Build versioning system**: SHA1-based version generation with caching
- **Comprehensive state management**: All textbox values stored as JSON in localStorage
- **API endpoints**: `/env-box` and `/client-box` for server-side data management
- **Visual feedback**: Offline styling for disabled textboxes during server unavailability
- **Console logging**: Debugging output for restoration and synchronization processes

### [Previous]
- Removed all textboxes from the `/env-id` endpoint page (`env-id.html`).
- The `/env-id` page now only displays the server env-id, client unique-id, and a reset button for the client-id.

## Architecture Notes

### Production Considerations
- **Database integration**: Replace in-memory storage with persistent database (PostgreSQL, Cloud SQL, etc.)
- **Redis/Memcached**: Consider caching layer for high-frequency updates
- **WebSocket support**: Real-time updates could be enhanced with WebSocket connections
- **Rate limiting**: Implement API rate limiting for production deployment
- **Authentication**: Add user authentication and authorization as needed
- **Monitoring**: Integrate with Cloud Monitoring for comprehensive observability

### Security Considerations
- **Input validation**: Implement server-side validation for textbox content
- **CSRF protection**: Add CSRF tokens for state-changing operations
- **Content filtering**: Sanitize user input to prevent XSS attacks
- **Rate limiting**: Prevent abuse of auto-save functionality

See the main page (`/`) for the complete textbox synchronization demo.

---
