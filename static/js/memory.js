// Memory management module for ICI Chat

const MemoryManager = {
  // Configuration
  SHARED_MEMORY_ENDPOINT: '/env-box',
  IP_MEMORY_ENDPOINT: '/ip-box',
  
  // Memory display and grouping logic
  displayMemoryWithGrouping: function(memoryArray, targetElementId) {
    const targetElement = document.getElementById(targetElementId);
    if (!targetElement) return;
    
    if (!Array.isArray(memoryArray) || memoryArray.length === 0) {
      targetElement.textContent = '';
      return;
    }
    
    // Group consecutive messages by sender
    const groups = [];
    let currentGroup = null;
    
    memoryArray.forEach(message => {
      if (!message || typeof message !== 'object') return;
      
      const sender = message.user || message.sender || 'Unknown';
      const text = message.text || message.message || '';
      const timestamp = message.timestamp || Date.now();
      
      if (!currentGroup || currentGroup.sender !== sender) {
        currentGroup = {
          sender: sender,
          messages: [],
          timestamp: timestamp
        };
        groups.push(currentGroup);
      }
      
      currentGroup.messages.push({
        text: text,
        timestamp: timestamp
      });
    });
    
    // Build display text with grouping
    let displayText = '';
    groups.forEach((group, groupIndex) => {
      if (groupIndex > 0) displayText += '\n';
      displayText += `${group.sender}:\n`;
      
      group.messages.forEach((msg, msgIndex) => {
        displayText += `  ${msg.text}`;
        if (msgIndex < group.messages.length - 1) displayText += '\n';
      });
      
      if (groupIndex < groups.length - 1) displayText += '\n';
    });
    
    targetElement.textContent = displayText;
  },

  // Load shared memory
  loadSharedMemory: async function(envId) {
    try {
      const response = await fetch(`${this.SHARED_MEMORY_ENDPOINT}?env_id=${envId}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
        const data = await response.json();
      const memories = data.value || [];
      this.displayMemoryWithGrouping(memories, 'env-box');
      return memories;
    } catch (error) {
      console.error('Error loading shared memory:', error);
      UIManager.updateStatus('shared', 'error', 'Failed to load shared memory');
      return [];
    }
  },

  // Load IP-shared memory
  loadIpMemory: async function(envId, publicIp) {
    try {
      const response = await fetch(`${this.IP_MEMORY_ENDPOINT}?env_id=${envId}&public_ip=${publicIp}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
        const data = await response.json();
      const memories = data.value || [];
      this.displayMemoryWithGrouping(memories, 'client-box');
      return memories;
    } catch (error) {
      console.error('Error loading IP memory:', error);
      UIManager.updateStatus('ip', 'error', 'Failed to load IP memory');
      return [];
    }
  },

  // Load private memory from localStorage
  loadPrivateMemory: function() {
    try {      const stored = localStorage.getItem('ici-private-memory');
      const memories = stored ? JSON.parse(stored) : [];
      this.displayMemoryWithGrouping(memories, 'private-box');
      return memories;
    } catch (error) {
      console.error('Error loading private memory:', error);
      return [];
    }
  },

  // Save memory to shared area
  saveToShared: async function(envId, message, user) {
    try {
      const newEntry = {
        text: message,
        user: user,
        timestamp: Date.now()
      };

      // Get current shared memory
      const currentMemories = await this.loadSharedMemory(envId);
      const updatedMemories = [...currentMemories, newEntry];

      const response = await fetch(this.SHARED_MEMORY_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          env_id: envId,
          value: updatedMemories
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Refresh display
      await this.loadSharedMemory(envId);
      
      // Update authenticated client display
      if (AuthManager && AuthManager.getUserId()) {
        UIManager.showAuthenticatedClient(AuthManager.getUserId());
      }
      
      UIManager.updateStatus('shared', 'success', 'Added to shared memory');
      return true;
    } catch (error) {
      console.error('Error saving to shared memory:', error);
      UIManager.updateStatus('shared', 'error', 'Failed to save to shared memory');
      return false;
    }
  },

  // Save memory to IP-shared area
  saveToIpShared: async function(envId, publicIp, message, user) {
    try {
      const newEntry = {
        text: message,
        user: user,
        timestamp: Date.now()
      };

      // Get current IP memory
      const currentMemories = await this.loadIpMemory(envId, publicIp);
      const updatedMemories = [...currentMemories, newEntry];

      const response = await fetch(this.IP_MEMORY_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          env_id: envId,
          public_ip: publicIp,
          value: updatedMemories
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      // Refresh display
      await this.loadIpMemory(envId, publicIp);
      
      // Update authenticated client display
      if (AuthManager && AuthManager.getUserId()) {
        UIManager.showAuthenticatedClient(AuthManager.getUserId());
      }
      
      UIManager.updateStatus('ip', 'success', 'Added to IP-shared memory');
      return true;
    } catch (error) {
      console.error('Error saving to IP memory:', error);
      UIManager.updateStatus('ip', 'error', 'Failed to save to IP memory');
      return false;
    }
  },

  // Save memory to private area
  saveToPrivate: function(message, user) {
    try {
      const newEntry = {
        text: message,
        user: user,
        timestamp: Date.now()
      };

      const currentMemories = this.loadPrivateMemory();
      const updatedMemories = [...currentMemories, newEntry];

      localStorage.setItem('ici-private-memory', JSON.stringify(updatedMemories));
      this.loadPrivateMemory(); // Refresh display
      
      // Update authenticated client display
      if (AuthManager && AuthManager.getUserId()) {
        UIManager.showAuthenticatedClient(AuthManager.getUserId());
      }
      
      UIManager.updateStatus('private', 'success', 'Added to private memory');
      return true;
    } catch (error) {
      console.error('Error saving to private memory:', error);
      UIManager.updateStatus('private', 'error', 'Failed to save to private memory');
      return false;
    }
  },

  // Clear all memories
  clearAllMemories: async function(envId, publicIp) {
    try {
      // Clear shared memory
      await fetch(this.SHARED_MEMORY_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          env_id: envId,
          value: []
        })
      });

      // Clear IP memory
      await fetch(this.IP_MEMORY_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          env_id: envId,
          public_ip: publicIp,
          value: []
        })
      });

      // Clear private memory
      localStorage.removeItem('ici-private-memory');

      // Refresh all displays
      await this.loadSharedMemory(envId);
      await this.loadIpMemory(envId, publicIp);
      this.loadPrivateMemory();

      UIManager.updateStatus('all', 'success', 'All memories cleared');
      return true;
    } catch (error) {
      console.error('Error clearing memories:', error);
      UIManager.updateStatus('all', 'error', 'Failed to clear memories');
      return false;
    }
  }
};
