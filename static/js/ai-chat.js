// AI Chat enhanced functionality with file uploads, screenshots, and offline caching
// filepath: e:\zip-myl-dev\ici\static\js\ai-chat.js

const AIChatManager = {
  uploadedFiles: [],
  
  init: function() {
    this.setupEventListeners();
    this.loadCachedInput();
    this.setupOfflineHandling();
  },

  setupEventListeners: function() {
    const aiSubmit = document.getElementById('ai-chat-submit');
    const aiInput = document.getElementById('ai-canvas');
    const aiResp = document.getElementById('ai-chat-response');
    const sysPromptBox = document.getElementById('system-prompt-box');
    const fileUploadBtn = document.getElementById('file-upload-btn');
    const fileUpload = document.getElementById('file-upload');
    const screenshotBtn = document.getElementById('screenshot-btn');

    // File upload button
    if (fileUploadBtn && fileUpload) {
      fileUploadBtn.addEventListener('click', () => {
        fileUpload.click();
      });

      fileUpload.addEventListener('change', (e) => {
        this.handleFileUpload(e.target.files);
      });
    }

    // Screenshot button
    if (screenshotBtn) {
      screenshotBtn.addEventListener('click', () => {
        this.handleScreenshot();
      });
    }

    // Enhanced AI Chat submit
    if (aiSubmit && aiInput && aiResp) {
      aiSubmit.onclick = async () => {
        await this.submitAIChat();
      };

      // Allow pressing Enter to submit (but Shift+Enter for newline)
      aiInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          aiSubmit.click();
        }
      });

      // Save input text as user types (preserve until manually deleted)
      aiInput.addEventListener('input', () => {
        this.saveInputToStorage();
      });

      aiInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter' && !e.shiftKey && aiInput.value.length > 0) {
          // Only on first use: update client-id to hash of initial-id + input
          if (!localStorage.getItem('ici-clientid-upgraded')) {
            const initialId = AuthManager.getUserId();
            const inputVal = aiInput.value;
            const newId = await hashStringToHex(initialId + inputVal);
            AuthManager.setUserId(newId);
            localStorage.setItem('ici-clientid-upgraded', '1');
            // Optionally, re-register client with backend
            const envId = AppState.envId;
            const publicIp = AppState.publicIp;
            if (envId && publicIp) {
              await APIManager.registerClient(envId, publicIp, newId);
            }
            // Update UI
            UIManager.showAuthenticatedClient(newId);
          }
        }
      });
    }
  },

  handleFileUpload: function(files) {
    for (let file of files) {
      const fileObj = {
        name: file.name,
        size: file.size,
        type: file.type,
        content: null,
        isImage: file.type.startsWith('image/')
      };

      // Read file content
      const reader = new FileReader();
      if (fileObj.isImage) {
        reader.onload = (e) => {
          fileObj.content = e.target.result; // Base64 data URL
          this.uploadedFiles.push(fileObj);
          this.updateFileDisplay();
        };
        reader.readAsDataURL(file);
      } else {
        reader.onload = (e) => {
          fileObj.content = e.target.result;
          this.uploadedFiles.push(fileObj);
          this.updateFileDisplay();
        };
        reader.readAsText(file);
      }
    }
  },

  handleScreenshot: async function() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
      alert('Screenshot feature requires HTTPS and a modern browser');
      return;
    }

    try {
      // Prompt user for screenshot type
      const choice = confirm('Take full screen screenshot?\nOK = Full Screen, Cancel = Select Area');
      
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { mediaSource: choice ? 'screen' : 'window' }
      });

      const video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      video.onloadedmetadata = () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        const dataURL = canvas.toDataURL('image/png');
        const fileObj = {
          name: `screenshot-${Date.now()}.png`,
          size: dataURL.length,
          type: 'image/png',
          content: dataURL,
          isImage: true,
          isScreenshot: true
        };

        this.uploadedFiles.push(fileObj);
        this.updateFileDisplay();
        
        // Stop the stream
        stream.getTracks().forEach(track => track.stop());
      };
    } catch (err) {
      console.error('Screenshot failed:', err);
      alert('Screenshot failed: ' + err.message);
    }
  },

  updateFileDisplay: function() {
    const uploadedFilesDiv = document.getElementById('uploaded-files');
    const fileList = document.getElementById('file-list');
    
    if (this.uploadedFiles.length > 0) {
      uploadedFilesDiv.style.display = 'block';
      fileList.innerHTML = this.uploadedFiles.map((file, index) => `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;padding:4px 8px;background:white;border-radius:4px;">
          <span style="font-size:0.9em;">
            ${file.isScreenshot ? '📷' : '📄'} ${file.name} 
            <span style="color:#6b7280;">(${this.formatFileSize(file.size)})</span>
          </span>
          <button onclick="AIChatManager.removeFile(${index})" style="border:none;background:#ef4444;color:white;border-radius:3px;padding:2px 6px;font-size:0.8em;cursor:pointer;">×</button>
        </div>
      `).join('');
    } else {
      uploadedFilesDiv.style.display = 'none';
    }
  },

  removeFile: function(index) {
    this.uploadedFiles.splice(index, 1);
    this.updateFileDisplay();
  },

  formatFileSize: function(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  submitAIChat: async function() {
    const aiInput = document.getElementById('ai-canvas');
    const aiResp = document.getElementById('ai-chat-response');
    const sysPromptBox = document.getElementById('system-prompt-box');
    const aiSubmit = document.getElementById('ai-chat-submit');
    
    const message = aiInput.value.trim();
    const systemPrompt = sysPromptBox ? sysPromptBox.value.trim() : '';
    
    if (!message && this.uploadedFiles.length === 0) {
      alert('Please enter a message or upload files');
      return;
    }

    // Don't clear the input - preserve user text until they manually delete it
    aiSubmit.disabled = true;
    aiResp.style.display = 'block';
    aiResp.textContent = 'Thinking...';

    try {
      // Prepare the request with files
      const requestData = {
        message: message,
        system_prompt: systemPrompt,
        files: this.uploadedFiles.map(file => ({
          name: file.name,
          type: file.type,
          content: file.content,
          isImage: file.isImage
        }))
      };

      // Check if online
      if (!navigator.onLine) {
        // Cache the request for later
        this.cacheOfflineRequest(requestData);
        aiResp.textContent = 'You are offline. Your request has been cached and will be sent when connection is restored.';
        document.getElementById('offline-cache-indicator').style.display = 'block';
        return;
      }

      const resp = await fetch('/ai-chat-enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData)
      });

      const data = await resp.json();
      const response = data.response || 'No response.';
      
      aiResp.textContent = response;
      
      // Cache the response
      this.cacheResponse(message, response, this.uploadedFiles);
      
      // Clear uploaded files after successful submission
      this.uploadedFiles = [];
      this.updateFileDisplay();
      
    } catch (e) {
      console.error('AI Chat error:', e);
      
      // Try to load from cache
      const cachedResponse = this.getCachedResponse(message);
      if (cachedResponse) {
        aiResp.textContent = `[CACHED] ${cachedResponse}`;
        document.getElementById('offline-cache-indicator').style.display = 'block';
      } else {
        aiResp.textContent = 'Error: ' + e.message;
      }
    } finally {
      aiSubmit.disabled = false;
    }
  },

  // Cache management
  saveInputToStorage: function() {
    const aiInput = document.getElementById('ai-canvas');
    if (aiInput) {
      localStorage.setItem('ici_ai_input', aiInput.value);
    }
  },

  loadCachedInput: function() {
    const aiInput = document.getElementById('ai-canvas');
    const cachedInput = localStorage.getItem('ici_ai_input');
    if (aiInput && cachedInput) {
      aiInput.value = cachedInput;
    }
  },

  cacheResponse: function(question, response, files) {
    const cache = JSON.parse(localStorage.getItem('ici_ai_cache') || '{}');
    const key = this.generateCacheKey(question, files);
    cache[key] = {
      response: response,
      timestamp: Date.now(),
      files: files.map(f => ({ name: f.name, type: f.type }))
    };
    localStorage.setItem('ici_ai_cache', JSON.stringify(cache));
  },

  getCachedResponse: function(question) {
    const cache = JSON.parse(localStorage.getItem('ici_ai_cache') || '{}');
    const key = this.generateCacheKey(question, this.uploadedFiles);
    return cache[key]?.response;
  },

  cacheOfflineRequest: function(requestData) {
    const offlineQueue = JSON.parse(localStorage.getItem('ici_offline_queue') || '[]');
    offlineQueue.push({
      ...requestData,
      timestamp: Date.now()
    });
    localStorage.setItem('ici_offline_queue', JSON.stringify(offlineQueue));
  },

  generateCacheKey: function(message, files) {
    const fileNames = files.map(f => f.name).sort().join('|');
    return `${message}|${fileNames}`;
  },

  setupOfflineHandling: function() {
    window.addEventListener('online', () => {
      this.processOfflineQueue();
      document.getElementById('offline-cache-indicator').style.display = 'none';
    });
  },

  processOfflineQueue: async function() {
    const offlineQueue = JSON.parse(localStorage.getItem('ici_offline_queue') || '[]');
    if (offlineQueue.length === 0) return;

    for (const requestData of offlineQueue) {
      try {
        const resp = await fetch('/ai-chat-enhanced', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData)
        });
        const data = await resp.json();
        this.cacheResponse(requestData.message, data.response, requestData.files);
      } catch (e) {
        console.error('Failed to process offline request:', e);
        break; // Stop processing if one fails
      }
    }

    // Clear the queue
    localStorage.setItem('ici_offline_queue', '[]');
  }
};

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => AIChatManager.init());
} else {
  AIChatManager.init();
}
