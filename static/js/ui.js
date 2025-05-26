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
  }
};
