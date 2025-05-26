// Debug utilities module for ICI Chat

const DebugManager = {
  // Debug configuration
  DEBUG_ENABLED: true,
  LOG_LEVELS: {
    ERROR: 0,
    WARN: 1,
    INFO: 2,
    DEBUG: 3
  },
  currentLogLevel: 2, // INFO by default

  // Initialize debug functionality
  init: function() {
    this.setupDebugUI();
    this.logStartup();
  },

  // Setup debug UI elements
  setupDebugUI: function() {
    const debugElement = document.getElementById('js-init-debug');
    if (debugElement && !this.DEBUG_ENABLED) {
      debugElement.style.display = 'none';
    }
  },

  // Log startup information
  logStartup: function() {
    this.log('DEBUG', 'ICI Chat modules loaded');
    this.log('INFO', `Environment: ${AppState.envId || 'unknown'}`);
    this.log('INFO', `User ID: ${AuthManager.getUserId() || 'not set'}`);
    this.log('INFO', `Connection: ${navigator.onLine ? 'online' : 'offline'}`);
  },

  // Generic logging function
  log: function(level, message, data = null) {
    if (!this.DEBUG_ENABLED) return;
    
    const levelValue = this.LOG_LEVELS[level] || this.LOG_LEVELS.INFO;
    if (levelValue > this.currentLogLevel) return;

    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${level}: ${message}`;

    switch (level) {
      case 'ERROR':
        console.error(logMessage, data);
        break;
      case 'WARN':
        console.warn(logMessage, data);
        break;
      case 'DEBUG':
        console.debug(logMessage, data);
        break;
      default:
        console.log(logMessage, data);
    }

    // Also log to debug UI if available
    this.updateDebugUI(logMessage);
  },

  // Update debug UI element
  updateDebugUI: function(message) {
    const debugElement = document.getElementById('js-init-debug');
    if (debugElement && this.DEBUG_ENABLED) {
      debugElement.textContent = message;
      
      // Auto-hide after 5 seconds for non-error messages
      if (!message.includes('ERROR')) {
        setTimeout(() => {
          if (debugElement.textContent === message) {
            debugElement.style.display = 'none';
          }
        }, 5000);
      }
    }
  },

  // Log error with stack trace
  logError: function(message, error) {
    this.log('ERROR', message, {
      error: error,
      stack: error?.stack,
      timestamp: Date.now()
    });
  },

  // Log API calls
  logApiCall: function(endpoint, method, data) {
    this.log('DEBUG', `API ${method} ${endpoint}`, data);
  },

  // Log memory operations
  logMemoryOperation: function(operation, area, success, data) {
    const level = success ? 'INFO' : 'ERROR';
    this.log(level, `Memory ${operation} (${area}): ${success ? 'success' : 'failed'}`, data);
  },

  // Log authentication events
  logAuthEvent: function(event, data) {
    this.log('INFO', `Auth: ${event}`, data);
  },

  // Performance timing
  startTimer: function(name) {
    if (this.DEBUG_ENABLED) {
      console.time(name);
    }
  },

  endTimer: function(name) {
    if (this.DEBUG_ENABLED) {
      console.timeEnd(name);
    }
  },

  // Get debug information
  getDebugInfo: function() {
    return {
      userAgent: navigator.userAgent,
      url: window.location.href,
      timestamp: new Date().toISOString(),
      appState: AppState,
      userId: AuthManager.getUserId(),
      isOnline: navigator.onLine,
      localStorage: {
        userId: localStorage.getItem('ici-chat-user-id'),
        authViaQR: localStorage.getItem('ici-auth-via-qr'),
        privateMemory: localStorage.getItem('ici-private-memory')
      }
    };
  },

  // Export debug information
  exportDebugInfo: function() {
    const debugInfo = this.getDebugInfo();
    const blob = new Blob([JSON.stringify(debugInfo, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ici-debug-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  },

  // Test all systems
  runSystemTest: async function() {
    this.log('INFO', 'Starting system test...');
    
    try {
      // Test server connection
      const serverOk = await APIManager.testServerConnection();
      this.log(serverOk ? 'INFO' : 'ERROR', `Server connection: ${serverOk ? 'OK' : 'FAILED'}`);

      // Test environment ID
      const envId = await APIManager.getEnvId();
      this.log(envId ? 'INFO' : 'ERROR', `Environment ID: ${envId ? 'OK' : 'FAILED'}`);

      // Test public IP
      const publicIp = await APIManager.getPublicIp();
      this.log(publicIp ? 'INFO' : 'ERROR', `Public IP: ${publicIp ? 'OK' : 'FAILED'}`);

      // Test memory systems
      await this.testMemorySystems();

      this.log('INFO', 'System test completed');
    } catch (error) {
      this.logError('System test failed', error);
    }
  },

  // Test memory systems
  testMemorySystems: async function() {
    try {
      // Test private memory
      const testMessage = `Test message ${Date.now()}`;
      MemoryManager.saveToPrivate(testMessage, 'test-user');
      const privateMemory = MemoryManager.loadPrivateMemory();
      this.log('INFO', `Private memory test: ${privateMemory.length > 0 ? 'OK' : 'FAILED'}`);

      // Test shared memory (if online)
      if (navigator.onLine && AppState.envId) {
        await MemoryManager.loadSharedMemory(AppState.envId);
        this.log('INFO', 'Shared memory test: OK');
      }

      // Test IP memory (if online)
      if (navigator.onLine && AppState.envId && AppState.publicIp) {
        await MemoryManager.loadIpMemory(AppState.envId, AppState.publicIp);
        this.log('INFO', 'IP memory test: OK');
      }
    } catch (error) {
      this.logError('Memory system test failed', error);
    }
  }
};
