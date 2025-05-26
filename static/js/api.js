// API communication module for ICI Chat

const APIManager = {
  // Base configuration
  BASE_URL: window.location.origin,
  
  // Get environment ID
  getEnvId: async function() {
    try {
      const response = await fetch('/env-id');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data.env_id;
    } catch (error) {
      console.error('Error getting environment ID:', error);
      return null;
    }
  },

  // Get public IP
  getPublicIp: async function() {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return data.ip;
    } catch (error) {
      console.error('Error getting public IP:', error);
      // Fallback to localhost for development
      return '127.0.0.1';
    }
  },

  // Register client with backend
  registerClient: async function(envId, publicIp, userId) {
    try {
      const response = await fetch('/client-register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          env_id: envId,
          public_ip: publicIp,
          client_id: userId,
          user_agent: navigator.userAgent,
          timestamp: Date.now()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('Client registered:', data);
      return data;
    } catch (error) {
      console.error('Error registering client:', error);
      return null;
    }
  },

  // Test server connectivity
  testServerConnection: async function() {
    try {
      const response = await fetch('/health');
      return response.ok;
    } catch (error) {
      console.error('Server connection test failed:', error);
      return false;
    }
  },

  // Get server status
  getServerStatus: async function() {
    try {
      const response = await fetch('/health');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.text();
    } catch (error) {
      console.error('Error getting server status:', error);
      return 'Server unavailable';
    }
  },

  // Generic API call wrapper
  makeRequest: async function(endpoint, options = {}) {
    try {
      const response = await fetch(endpoint, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  },

  // Submit lost memory report
  submitLostMemoryReport: async function(envId, report) {
    try {
      const response = await fetch('/lost-memory-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          env_id: envId,
          report: report,
          timestamp: Date.now()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting lost memory report:', error);
      throw error;
    }
  },

  // Get client data for recovery
  getClientData: async function(envId) {
    try {
      const response = await fetch(`/recovery-data?env_id=${envId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting client data:', error);
      return null;
    }
  }
};
