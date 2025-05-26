// Main application module for ICI Chat

// Global application state
const AppState = {
  envId: null,
  publicIp: null,
  initialized: false
};

// Main application manager
const AppManager = {
  // Initialize the application
  init: async function() {
    try {
      DebugManager.init();
      DebugManager.log('INFO', 'Initializing ICI Chat application...');
      
      // Initialize UI first
      UIManager.init();
      
      // Initialize authentication
      AuthManager.init();
      
      // Handle authentication from URL if present
      AuthManager.handleAuthFromUrl();
      
      // If authenticated, continue with full initialization
      if (AuthManager.isAuthenticated() && localStorage.getItem('ici-auth-via-qr') === 'true') {
        await this.initializeAfterAuth();
      }
      
      DebugManager.log('INFO', 'Application initialization complete');
    } catch (error) {
      DebugManager.logError('Application initialization failed', error);
      UIManager.updateStatus('all', 'error', 'Failed to initialize application');
    }
  },

  // Initialize after authentication
  initializeAfterAuth: async function() {
    try {
      DebugManager.log('INFO', 'Initializing authenticated session...');
      
      // Get environment ID
      AppState.envId = await APIManager.getEnvId();
      if (!AppState.envId) {
        throw new Error('Failed to get environment ID');
      }
      
      // Get public IP
      AppState.publicIp = await APIManager.getPublicIp();
      if (!AppState.publicIp) {
        DebugManager.log('WARN', 'Failed to get public IP, using fallback');
        AppState.publicIp = '127.0.0.1';
      }
      
      DebugManager.log('INFO', `Environment ID: ${AppState.envId}`);
      DebugManager.log('INFO', `Public IP: ${AppState.publicIp}`);
      
      // Register client with backend
      await APIManager.registerClient(AppState.envId, AppState.publicIp, AuthManager.getUserId());
      
      // Load all memory areas
      await this.loadAllMemories();
      
      // Mark as initialized
      AppState.initialized = true;
      
      DebugManager.log('INFO', 'Authenticated session initialization complete');
    } catch (error) {
      DebugManager.logError('Authenticated session initialization failed', error);
      UIManager.updateStatus('all', 'error', 'Failed to initialize session');
    }
  },

  // Load all memory areas
  loadAllMemories: async function() {
    try {
      DebugManager.log('INFO', 'Loading all memory areas...');
      
      // Load memories in parallel
      await Promise.all([
        MemoryManager.loadSharedMemory(AppState.envId),
        MemoryManager.loadIpMemory(AppState.envId, AppState.publicIp),
        MemoryManager.loadPrivateMemory()
      ]);
      
      DebugManager.log('INFO', 'All memory areas loaded successfully');
    } catch (error) {
      DebugManager.logError('Failed to load memory areas', error);
      UIManager.updateStatus('all', 'error', 'Failed to load memories');
    }
  },

  // Handle visibility change (tab switching)
  handleVisibilityChange: function() {
    if (!document.hidden && AppState.initialized) {
      // Refresh memories when tab becomes visible
      UIManager.refreshAllMemories();
    }
  },

  // Handle online/offline events
  handleConnectionChange: function(isOnline) {
    DebugManager.log('INFO', `Connection status changed: ${isOnline ? 'online' : 'offline'}`);
    
    if (isOnline && AppState.initialized) {
      // Refresh memories when coming back online
      setTimeout(() => {
        UIManager.refreshAllMemories();
      }, 1000);
    }
  }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  // Show initial debug info
  UIManager.showDebugInfo('JS loaded: DOMContentLoaded fired.');
  
  // Initialize the application
  AppManager.init();
  
  // Setup additional event listeners
  document.addEventListener('visibilitychange', AppManager.handleVisibilityChange);
  
  window.addEventListener('online', () => {
    UIManager.updateConnectionStatus(true);
    AppManager.handleConnectionChange(true);
  });
  
  window.addEventListener('offline', () => {
    UIManager.updateConnectionStatus(false);
    AppManager.handleConnectionChange(false);
  });
  
  // Hide debug info after initialization
  setTimeout(() => {
    UIManager.hideDebugInfo();
  }, 3000);
});

// Legacy functions for backward compatibility
function showMemorySection() {
  UIManager.showMemorySection();
}

function addMemoryToShared() {
  const textarea = document.getElementById('shared-memory-textarea');
  const message = textarea?.value?.trim();
  if (message && AuthManager.getUserId()) {
    MemoryManager.saveToShared(AppState.envId, message, AuthManager.getUserId());
    textarea.value = '';
  }
}

function addMemoryToIp() {
  const textarea = document.getElementById('ip-memory-textarea');
  const message = textarea?.value?.trim();
  if (message && AuthManager.getUserId() && AppState.publicIp) {
    MemoryManager.saveToIpShared(AppState.envId, AppState.publicIp, message, AuthManager.getUserId());
    textarea.value = '';
  }
}

function addMemoryToPrivate() {
  const textarea = document.getElementById('private-memory-textarea');
  const message = textarea?.value?.trim();
  if (message && AuthManager.getUserId()) {
    MemoryManager.saveToPrivate(message, AuthManager.getUserId());
    textarea.value = '';
  }
}
