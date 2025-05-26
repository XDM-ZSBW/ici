// UI management module for ICI Chat

const UIManager = {
  // Initialize UI components
  init: function() {
    this.setupEventListeners();
    this.showMemorySection();
    this.initializeStatusIndicators();
  },

  // Show memory section (always visible for demo)
  showMemorySection: function() {
    const memorySection = document.getElementById('memory-section');
    if (memorySection) {
      memorySection.style.display = '';
    }
  },
  // Setup event listeners for UI interactions
  setupEventListeners: function() {
    // Add to shared memory button
    const addSharedBtn = document.getElementById('add-to-shared');
    if (addSharedBtn) {
      addSharedBtn.addEventListener('click', () => {
        const input = document.getElementById('memory-input');
        const message = input?.value?.trim();
        if (message && AuthManager.getUserId()) {
          MemoryManager.saveToShared(AppState.envId, message, AuthManager.getUserId());
          input.value = '';
        }
      });
    }

    // Add to IP-shared memory button
    const addIpBtn = document.getElementById('add-to-ip');
    if (addIpBtn) {
      addIpBtn.addEventListener('click', () => {
        const input = document.getElementById('memory-input');
        const message = input?.value?.trim();
        if (message && AuthManager.getUserId() && AppState.publicIp) {
          MemoryManager.saveToIpShared(AppState.envId, AppState.publicIp, message, AuthManager.getUserId());
          input.value = '';
        }
      });
    }

    // Add to private memory button
    const addPrivateBtn = document.getElementById('add-to-private');
    if (addPrivateBtn) {
      addPrivateBtn.addEventListener('click', () => {
        const input = document.getElementById('memory-input');
        const message = input?.value?.trim();
        if (message && AuthManager.getUserId()) {
          MemoryManager.saveToPrivate(message, AuthManager.getUserId());
          input.value = '';
        }
      });
    }

    // Debug buttons
    const refreshBtn = document.getElementById('debug-refresh');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.refreshAllMemories();
      });
    }

    const testSyncBtn = document.getElementById('debug-test-sync');
    if (testSyncBtn) {
      testSyncBtn.addEventListener('click', () => {
        this.testSync();
      });
    }

    const clearAllBtn = document.getElementById('debug-clear-all');
    if (clearAllBtn) {
      clearAllBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to clear all memories? This cannot be undone.')) {
          MemoryManager.clearAllMemories(AppState.envId, AppState.publicIp);
        }
      });
    }

    const testApiBtn = document.getElementById('debug-test-api');
    if (testApiBtn) {
      testApiBtn.addEventListener('click', () => {
        DebugManager.runSystemTest();
      });
    }

    // Screenshot (camera) button
    const screenshotBtn = document.getElementById('screenshot-btn');
    if (screenshotBtn) {
      screenshotBtn.addEventListener('click', async () => {
        // Prompt user for screenshot type
        const choice = await UIManager.promptScreenshotType();
        if (!choice) return;
        if (choice === 'screen') {
          UIManager.captureFullScreen();
        } else if (choice === 'area') {
          UIManager.captureArea();
        }
      });
    }
  },

  // Initialize status indicators
  initializeStatusIndicators: function() {
    this.updateConnectionStatus(navigator.onLine);
    
    // Listen for online/offline events
    window.addEventListener('online', () => {
      this.updateConnectionStatus(true);
    });
    
    window.addEventListener('offline', () => {
      this.updateConnectionStatus(false);
    });
  },

  // Update connection status indicator
  updateConnectionStatus: function(isOnline) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
      indicator.textContent = isOnline ? 'Online' : 'Offline';
      indicator.className = `status-indicator ${isOnline ? 'online' : 'offline'}`;
    }
  },

  // Update memory area status
  updateStatus: function(area, type, message) {
    const statusId = `${area}-status`;
    const statusElement = document.getElementById(statusId);
    
    if (statusElement) {
      statusElement.textContent = message;
      statusElement.className = `memory-status ${type}`;
      
      // Clear status after 3 seconds
      setTimeout(() => {
        statusElement.textContent = '';
        statusElement.className = 'memory-status';
      }, 3000);
    }
  },
  // Show authentication section
  showAuthPrompt: function() {
    const authSection = document.getElementById('auth-section');
    
    if (authSection) authSection.style.display = '';
  },

  // Show memory section (chat section removed)
  showChat: function() {
    const authSection = document.getElementById('auth-section');
    
    if (authSection) authSection.style.display = 'none';
  },

  // Update QR code and auth link
  updateAuthUI: function(userId) {
    const qrCodeImg = document.getElementById('qr-code-img');
    const authLink = document.getElementById('auth-link');
    
    if (userId) {
      const authUrl = window.location.origin + '/client/' + userId;
      
      if (authLink) {
        authLink.href = authUrl;
        authLink.textContent = 'open authentication link';
      }
      
      if (qrCodeImg) {
        qrCodeImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + encodeURIComponent(authUrl);
      }
    }
  },

  // Refresh all memory areas
  refreshAllMemories: async function() {
    this.updateStatus('all', 'info', 'Refreshing memories...');
    
    try {
      await Promise.all([
        MemoryManager.loadSharedMemory(AppState.envId),
        MemoryManager.loadIpMemory(AppState.envId, AppState.publicIp),
        MemoryManager.loadPrivateMemory()
      ]);
      
      this.updateStatus('all', 'success', 'All memories refreshed');
    } catch (error) {
      console.error('Error refreshing memories:', error);
      this.updateStatus('all', 'error', 'Failed to refresh memories');
    }
  },

  // Test sync functionality
  testSync: async function() {
    this.updateStatus('all', 'info', 'Testing sync...');
    
    try {
      const testMessage = `Test sync at ${new Date().toLocaleTimeString()}`;
      const userId = AuthManager.getUserId();
      
      await MemoryManager.saveToShared(AppState.envId, testMessage, userId);
      this.updateStatus('all', 'success', 'Sync test completed');
    } catch (error) {
      console.error('Sync test failed:', error);
      this.updateStatus('all', 'error', 'Sync test failed');
    }
  },

  // Show debug information
  showDebugInfo: function(message) {
    const debugElement = document.getElementById('js-init-debug');
    if (debugElement) {
      debugElement.style.display = '';
      debugElement.textContent = message;
    }
  },

  // Hide debug information
  hideDebugInfo: function() {
    const debugElement = document.getElementById('js-init-debug');
    if (debugElement) {
      debugElement.style.display = 'none';
    }
  },

  // Add screenshot helpers to UIManager
  promptScreenshotType: function() {
    return new Promise((resolve) => {
      // Simple modal prompt
      const modal = document.createElement('div');
      modal.style.position = 'fixed';
      modal.style.top = '0';
      modal.style.left = '0';
      modal.style.width = '100vw';
      modal.style.height = '100vh';
      modal.style.background = 'rgba(0,0,0,0.35)';
      modal.style.display = 'flex';
      modal.style.alignItems = 'center';
      modal.style.justifyContent = 'center';
      modal.style.zIndex = '9999';
      modal.innerHTML = `
        <div style="background:#fff;padding:32px 28px;border-radius:12px;box-shadow:0 2px 16px #0002;text-align:center;min-width:260px;">
          <div style="font-size:1.15em;margin-bottom:18px;">Take screenshot of:</div>
          <button id="ss-whole" style="margin:8px 0 0 0;padding:10px 18px;font-size:1em;border-radius:8px;border:2px solid #e5e7eb;background:#f3f4f6;cursor:pointer;">🖥️ Whole Screen</button><br>
          <button id="ss-area" style="margin:10px 0 0 0;padding:10px 18px;font-size:1em;border-radius:8px;border:2px solid #e5e7eb;background:#f3f4f6;cursor:pointer;">✏️ Select Area</button><br>
          <button id="ss-cancel" style="margin:18px 0 0 0;padding:8px 16px;font-size:0.95em;border-radius:8px;border:2px solid #e5e7eb;background:#fff;cursor:pointer;">Cancel</button>
        </div>
      `;
      document.body.appendChild(modal);
      modal.querySelector('#ss-whole').onclick = () => { document.body.removeChild(modal); resolve('screen'); };
      modal.querySelector('#ss-area').onclick = () => { document.body.removeChild(modal); resolve('area'); };
      modal.querySelector('#ss-cancel').onclick = () => { document.body.removeChild(modal); resolve(null); };
    });
  },

  captureFullScreen: async function() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      alert('Screen capture is not supported in this browser or requires HTTPS.');
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      const track = stream.getVideoTracks()[0];
      const imageCapture = new ImageCapture(track);
      const bitmap = await imageCapture.grabFrame();
      // Draw to canvas
      const canvas = document.createElement('canvas');
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(bitmap, 0, 0);
      // Stop the stream
      track.stop();
      // Show preview or handle image
      UIManager.showScreenshotPreview(canvas.toDataURL('image/png'));
    } catch (err) {
      alert('Failed to capture screen: ' + err);
    }
  },

  captureArea: async function() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      alert('Screen capture is not supported in this browser or requires HTTPS.');
      return;
    }
    // Use full screen capture, then let user draw a rectangle overlay
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      const track = stream.getVideoTracks()[0];
      const imageCapture = new ImageCapture(track);
      const bitmap = await imageCapture.grabFrame();
      track.stop();
      // Draw to canvas
      const canvas = document.createElement('canvas');
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(bitmap, 0, 0);
      // Overlay for area selection
      UIManager.showAreaSelector(canvas, (croppedDataUrl) => {
        UIManager.showScreenshotPreview(croppedDataUrl);
      });
    } catch (err) {
      alert('Failed to capture screen: ' + err);
    }
  },

  showAreaSelector: function(fullCanvas, callback) {
    // Overlay a semi-transparent div for area selection
    const overlay = document.createElement('div');
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100vw';
    overlay.style.height = '100vh';
    overlay.style.zIndex = '10000';
    overlay.style.cursor = 'crosshair';
    overlay.style.background = 'rgba(0,0,0,0.15)';
    document.body.appendChild(overlay);

    let startX, startY, endX, endY, rect;
    const selection = document.createElement('div');
    selection.style.position = 'absolute';
    selection.style.border = '2px dashed #2563eb';
    selection.style.background = 'rgba(37,99,235,0.08)';
    overlay.appendChild(selection);

    function mouseDown(e) {
      startX = e.clientX; startY = e.clientY;
      selection.style.left = startX + 'px';
      selection.style.top = startY + 'px';
      selection.style.width = '0px';
      selection.style.height = '0px';
      overlay.addEventListener('mousemove', mouseMove);
      overlay.addEventListener('mouseup', mouseUp);
    }
    function mouseMove(e) {
      endX = e.clientX; endY = e.clientY;
      const x = Math.min(startX, endX);
      const y = Math.min(startY, endY);
      const w = Math.abs(endX - startX);
      const h = Math.abs(endY - startY);
      selection.style.left = x + 'px';
      selection.style.top = y + 'px';
      selection.style.width = w + 'px';
      selection.style.height = h + 'px';
    }
    function mouseUp(e) {
      overlay.removeEventListener('mousemove', mouseMove);
      overlay.removeEventListener('mouseup', mouseUp);
      document.body.removeChild(overlay);
      // Crop the canvas
      const scaleX = fullCanvas.width / window.innerWidth;
      const scaleY = fullCanvas.height / window.innerHeight;
      const x = Math.round(Math.min(startX, e.clientX) * scaleX);
      const y = Math.round(Math.min(startY, e.clientY) * scaleY);
      const w = Math.round(Math.abs(e.clientX - startX) * scaleX);
      const h = Math.round(Math.abs(e.clientY - startY) * scaleY);
      const cropped = document.createElement('canvas');
      cropped.width = w;
      cropped.height = h;
      const ctx = cropped.getContext('2d');
      ctx.drawImage(fullCanvas, x, y, w, h, 0, 0, w, h);
      callback(cropped.toDataURL('image/png'));
    }
    overlay.addEventListener('mousedown', mouseDown);
  },

  showScreenshotPreview: function(dataUrl) {
    // Show a modal with the screenshot preview
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(0,0,0,0.45)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '9999';
    modal.innerHTML = `
      <div style="background:#fff;padding:24px 18px;border-radius:12px;box-shadow:0 2px 16px #0002;text-align:center;min-width:260px;">
        <div style="font-size:1.1em;margin-bottom:12px;">Screenshot Preview</div>
        <img src="${dataUrl}" style="max-width:420px;max-height:320px;border-radius:8px;border:1px solid #e5e7eb;box-shadow:0 1px 6px #0001;" />
        <div style="margin-top:16px;">
          <a href="${dataUrl}" download="screenshot.png" style="padding:8px 16px;font-size:0.95em;border-radius:8px;border:2px solid #e5e7eb;background:#f3f4f6;cursor:pointer;text-decoration:none;">Download</a>
          <button style="margin-left:12px;padding:8px 16px;font-size:0.95em;border-radius:8px;border:2px solid #e5e7eb;background:#fff;cursor:pointer;" onclick="this.closest('div[style*='background:#fff']').parentNode.remove()">Close</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }
};
