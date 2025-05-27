// Authentication management module for ICI Chat

const AuthManager = {
  // Storage keys
  USER_ID_KEY: 'ici-chat-user-id',
  AUTH_VIA_QR_KEY: 'ici-auth-via-qr',

  // Initialize authentication
  init: function() {
    this.userId = localStorage.getItem(this.USER_ID_KEY);
    this.checkAuthStatus();
  },

  // Generate a new user ID
  generateUserId: function() {
    return 'u-' + Math.random().toString(36).slice(2, 12) + Date.now().toString(36);
  },

  // Get current user ID
  getUserId: function() {
    return this.userId;
  },

  // Set user ID and save to localStorage
  setUserId: function(userId) {
    this.userId = userId;
    localStorage.setItem(this.USER_ID_KEY, userId);
  },

  // Check if user is authenticated
  isAuthenticated: function() {
    return !!this.userId;
  },

  // Check authentication status and show appropriate UI
  checkAuthStatus: function() {
    if (!this.userId) {
      this.userId = this.generateUserId();
      this.setUserId(this.userId);
    }    // Check if authenticated via QR code
    const authViaQR = localStorage.getItem(this.AUTH_VIA_QR_KEY);
    
    if (authViaQR === 'true') {
      // User has been authenticated via QR code, show chat
      UIManager.showChat();
      UIManager.showAuthenticatedClient(this.userId);
      
      // Initialize app after authentication
      if (typeof AppManager !== 'undefined') {
        AppManager.initializeAfterAuth();
      }
    } else {
      // Show authentication prompt
      UIManager.showAuthPrompt();
      UIManager.updateAuthUI(this.userId);
      UIManager.hideAuthenticatedClient();
    }
  },

  // Handle successful authentication
  onAuthenticationSuccess: function() {
    localStorage.setItem(this.AUTH_VIA_QR_KEY, 'true');
    UIManager.showChat();
    
    // Show authenticated client display
    UIManager.showAuthenticatedClient(this.userId);
    
    // Initialize app after authentication
    if (typeof AppManager !== 'undefined') {
      AppManager.initializeAfterAuth();
    }
  },

  // Handle authentication via URL (QR code scan)
  handleAuthFromUrl: function() {
    const urlParams = new URLSearchParams(window.location.search);
    const authToken = urlParams.get('auth');
    
    if (authToken) {
      // Validate token and authenticate user
      this.validateAuthToken(authToken);
    }
  },

  // Validate authentication token
  validateAuthToken: function(token) {
    // In a real implementation, this would validate the token with the server
    // For demo purposes, we'll just check if it matches our user ID pattern
    if (token && token.startsWith('u-')) {
      this.setUserId(token);
      this.onAuthenticationSuccess();
      
      // Remove auth parameter from URL
      const url = new URL(window.location);
      url.searchParams.delete('auth');
      window.history.replaceState({}, document.title, url.pathname);
    }
  },

  // Clear authentication data
  clearAuth: function() {
    localStorage.removeItem(this.USER_ID_KEY);
    localStorage.removeItem(this.AUTH_VIA_QR_KEY);
    this.userId = null;
    UIManager.showAuthPrompt();
  },

  // Get authentication URL for QR code
  getAuthUrl: function() {
    return `${window.location.origin}/client/${this.userId}`;
  },

  // Handle client authentication endpoint
  authenticateClient: function(clientId) {
    // This is called when user visits /client/<userId>
    this.setUserId(clientId);
    localStorage.setItem(this.AUTH_VIA_QR_KEY, 'true');
    
    // Show authenticated client display
    UIManager.showAuthenticatedClient(clientId);
    
    // Navigate back to chat
    window.location.href = '/chat';
  }
};
