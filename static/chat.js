// chat.js
// ICI Chat: Shared (server) and private (localStorage) memory chat

document.addEventListener('DOMContentLoaded', function() {
  var jsDebug = document.getElementById('js-init-debug');
  if (jsDebug) {
    jsDebug.style.display = '';
    jsDebug.textContent = 'JS loaded: DOMContentLoaded fired.';
  }
  // Always show memory section for demo (moved from earlier in the script)
  showMemorySection();
  if (jsDebug) jsDebug.textContent += ' showMemorySection() called.';
  
  const authSection = document.getElementById('auth-section');
  const chatSection = document.getElementById('chat-section');
  const sharedChatHistory = document.getElementById('shared-chat-history');
  const privateChatHistory = document.getElementById('private-chat-history');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const qrCodeImg = document.getElementById('qr-code-img');
  const authLink = document.getElementById('auth-link');

  // --- Auth logic ---
  // Use a localStorage key for user_id; if not present, require authentication
  const USER_ID_KEY = 'ici-chat-user-id';
  let userId = localStorage.getItem(USER_ID_KEY);

  function generateUserId() {
    // Simple random string, not cryptographically secure
    return 'u-' + Math.random().toString(36).slice(2, 12) + Date.now().toString(36);
  }

  function showAuthPrompt() {
    authSection.style.display = '';
    chatSection.style.display = 'none';
    // Generate a QR code for authentication (link to /client/<userId>)
    if (!userId) userId = generateUserId();
    const authUrl = window.location.origin + '/client/' + userId;
    authLink.href = authUrl;
    authLink.textContent = 'open authentication link';
    // Use a free QR code API for demo
    qrCodeImg.src = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + encodeURIComponent(authUrl);
  }

  function showChat() {
    authSection.style.display = 'none';
    chatSection.style.display = '';
  }
  // Add a flag to track if authenticated via QR code
  const AUTH_VIA_QR_KEY = 'ici-auth-via-qr';
    // --- Enhanced memory display with grouping and weaving ---
  function formatMemoryDisplay(messages, memoryType) {
    if (!Array.isArray(messages) || messages.length === 0) {
      return `${getMemoryTypeHeader(memoryType)}\n(No memories yet)`;
    }
    
    // Group messages by user and sort by timestamp
    const sortedMessages = messages.sort((a, b) => (a.ts || 0) - (b.ts || 0));
    const groupedByUser = {};
    
    sortedMessages.forEach(msg => {
      const user = msg.user || 'Unknown';
      if (!groupedByUser[user]) {
        groupedByUser[user] = [];
      }
      groupedByUser[user].push(msg);
    });
    
    // Create display with user grouping
    let content = getMemoryTypeHeader(memoryType);
    const users = Object.keys(groupedByUser);
    
    if (users.length === 1) {
      // Single user - simple list
      content += '\n' + sortedMessages.map(m => 
        `• ${m.q}${m.a ? '\n  ↳ ' + m.a : ''}`
      ).join('\n');
    } else {
      // Multiple users - weave by timestamp but show user context
      content += '\n';
      sortedMessages.forEach((msg, index) => {
        const prevMsg = sortedMessages[index - 1];
        const showUser = !prevMsg || prevMsg.user !== msg.user;
        
        if (showUser) {
          content += `\n[${msg.user || 'Unknown'}]\n`;
        }
        content += `• ${msg.q}${msg.a ? '\n  ↳ ' + msg.a : ''}\n`;
      });
    }
    
    return content;
  }
  
  function getMemoryTypeHeader(memoryType) {
    switch (memoryType) {
      case 'shared':
        return 'SHARED MEMORY (All Users)\n' + '='.repeat(30);
      case 'ip-shared':
        return 'IP-SHARED MEMORY (Same Network)\n' + '='.repeat(35);
      case 'private':
        return 'PRIVATE MEMORY (This Browser)\n' + '='.repeat(32);
      default:
        return 'MEMORY\n' + '='.repeat(10);
    }
  }
  
  // --- Offline/Online detection and status management ---
  let isServerOnline = true;
  let offlineDetectionTimer = null;
  
  function updateServerStatus(online) {
    if (isServerOnline === online) return; // No change
    
    isServerOnline = online;
    console.log(`Server status changed: ${online ? 'ONLINE' : 'OFFLINE'}`);
    
    // Update visual indicators
    const sharedStatus = document.getElementById('shared-status');
    const ipStatus = document.getElementById('ip-status');
    const envBox = document.getElementById('env-box');
    const clientBox = document.getElementById('client-box');
    
    if (sharedStatus) {
      sharedStatus.className = online ? '' : 'offline';
    }
    if (ipStatus) {
      ipStatus.className = online ? '' : 'offline';
    }
    if (envBox) {
      envBox.className = `memory-textarea ${online ? '' : 'offline'}`;
    }
    if (clientBox) {
      clientBox.className = `memory-textarea ${online ? '' : 'offline'}`;
    }
    
    // If coming back online, trigger resync
    if (online) {
      console.log('Server back online - triggering resync...');
      setTimeout(() => {
        uploadMissingPrivateToShared(true);
      }, 1000);
    }
  }
  
  function checkServerConnection() {
    fetch('/env-id', { method: 'HEAD' })
      .then(() => updateServerStatus(true))
      .catch(() => updateServerStatus(false));
  }
    // --- Enhanced memory population with error handling ---
  function populateMemorySectionTextareas() {
    console.log('=== populateMemorySectionTextareas called ===');
    const envBox = document.getElementById('env-box');
    const clientBox = document.getElementById('client-box');
    const privateBox = document.getElementById('private-box');
    
    console.log('Elements found:', { 
      envBox: !!envBox, 
      clientBox: !!clientBox, 
      privateBox: !!privateBox,
      envBoxValue: envBox ? envBox.value.substring(0, 50) + '...' : 'null'
    });
    
    // env-box: shared memory (all users, same env-id)
    if (envBox) {
      console.log('Fetching env-box data...');
      fetch('/env-box?env_id=ici-demo')
        .then(r => {
          console.log('Response status:', r.status, r.statusText);
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then(data => {
          console.log('env-box data received:', data);
          const messages = Array.isArray(data.value) ? data.value : [];
          console.log('Parsed messages array length:', messages.length);
          const formattedDisplay = formatMemoryDisplay(messages, 'shared');
          console.log('Formatted display (first 100 chars):', formattedDisplay.substring(0, 100));
          envBox.value = formattedDisplay;
          console.log('env-box.value set to length:', envBox.value.length);
          updateServerStatus(true);
          console.log('env-box populated successfully');
        })
        .catch(err => {
          console.log('env-box fetch error:', err);
          envBox.value = formatMemoryDisplay([], 'shared') + '\n\n(Failed to load - server may be offline)';
          updateServerStatus(false);
        });
    } else {
      console.log('env-box element not found!');
    }
      
    // client-box: fetch from backend if available
    if (clientBox) {
      fetch('/client-box?env_id=ici-demo')
        .then(r => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.json();
        })
        .then(data => {
          const messages = Array.isArray(data.value) ? data.value : [];
          clientBox.value = formatMemoryDisplay(messages, 'ip-shared');
          updateServerStatus(true);
        })
        .catch(err => {
          console.log('client-box fetch error:', err);
          clientBox.value = formatMemoryDisplay([], 'ip-shared') + '\n\n(Failed to load - server may be offline)';
          updateServerStatus(false);
        });
    }
    
    // private-box: localStorage private chat
    if (privateBox) {
      try {
        const arr = JSON.parse(localStorage.getItem('ici-private-chat-' + userId) || '[]');
        privateBox.value = formatMemoryDisplay(arr, 'private');
      } catch (err) {
        console.log('private-box load error:', err);
        privateBox.value = formatMemoryDisplay([], 'private') + '\n\n(Failed to load from local storage)';
      }
    }
  }

  function showMemorySection() {
    document.getElementById('chat-section').style.display = 'none';
    document.getElementById('memory-section').style.display = '';
    populateMemorySectionTextareas();
  }
  function showChatSection() {
    document.getElementById('memory-section').style.display = 'none';
    document.getElementById('chat-section').style.display = '';
  }  // Check authentication - for demo, always show memory section
  if (!userId) {
    userId = generateUserId();
    localStorage.setItem(USER_ID_KEY, userId);
  }
  // Always show memory section for demo - but wait for DOM to be ready
  // This will be called in the consolidated DOMContentLoaded handler

  localStorage.setItem(USER_ID_KEY, userId);

  // Listen for authentication (user visits /client/<userId> and sets email)
  window.addEventListener('storage', function(e) {
    if (e.key === USER_ID_KEY && e.newValue) {
      userId = e.newValue;
      // If authenticated via QR, show memory section instead of chat
      if (localStorage.getItem(AUTH_VIA_QR_KEY) === '1') {
        showMemorySection();
      } else {
        showChatSection();
      }
    }
  });

  // --- Chat logic ---
  // Private chat in localStorage
  const PRIVATE_CHAT_KEY = 'ici-private-chat-' + userId;
  function getPrivateChat() {
    try {
      return JSON.parse(localStorage.getItem(PRIVATE_CHAT_KEY) || '[]');
    } catch { return []; }
  }
  function setPrivateChat(arr) {
    localStorage.setItem(PRIVATE_CHAT_KEY, JSON.stringify(arr));
  }
  function renderPrivateChat() {
    try {
      const arr = getPrivateChat();
      // For private memory, treat user as 'You' if not set
      const arrWithUser = arr.map(msg => ({...msg, user: msg.user || 'You'}));
      const groups = aggregateAndWeaveChats(arrWithUser);
      privateChatHistory.innerHTML = '<b>Private Memory (Grouped by Minute)</b><br>' +
        groups.map(group => {
          let html = `<div class=\"chat-group\"><span style='font-weight:bold;color:#2a5298;'>${group.user}</span> <span style='color:#888;'>[${group.minute}]</span><ul style='margin:0 0 8px 18px;padding:0;'>`;
          for (const msg of group.messages) {
            html += `<li><span style='color:#333;'>Q:</span> ${msg.q}`;
            if (msg.a && msg.a.trim()) {
              html += ` <span style='color:#007700;'>A:</span> ${msg.a}`;
            }
            html += '</li>';
          }
          html += '</ul></div>';
          return html;
        }).join('');
      var errEl = document.getElementById('private-chat-error');
      if (errEl) errEl.style.display = 'none';
      if (typeof scrollPrivate === 'function') scrollPrivate();
    } catch (e) {
      var errEl = document.getElementById('private-chat-error');
      if (errEl) {
        errEl.textContent = 'Failed to load private memory.';
        errEl.style.display = '';
      }
    }
  }  // Shared chat via server
  function getSharedChat() {
    return fetch('/env-box?env_id=ici-demo', { method: 'GET' })
      .then(r => r.json())
      .then(data => Array.isArray(data.value) ? data.value : [])
      .catch(() => []);
  }
  function setSharedChat(arr) {
    // Always POST the full array (running total)
    // Ensure every message has a user field
    const arrWithUser = arr.map(msg => ({...msg, user: msg.user || userId || 'Anonymous'}));
    return fetch('/env-box?env_id=ici-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: arrWithUser })
    });
  }
  
  function renderSharedChat() {
    try {
      getSharedChat().then(arr => {
        // For shared memory, show all users
        const groups = aggregateAndWeaveChats(arr);
        sharedChatHistory.innerHTML = '<b>Shared Memory (Grouped by Minute)</b><br>' +
          (groups.length === 0 ? '<i>No shared messages yet. Start a conversation!</i>' :
          groups.map(group => {
            let html = `<div class="chat-group"><span style='font-weight:bold;color:#2a5298;'>${group.user}</span> <span style='color:#888;'>[${group.minute}]</span><ul style='margin:0 0 8px 18px;padding:0;'>`;
            for (const msg of group.messages) {
              html += `<li><span style='color:#333;'>Q:</span> ${msg.q}`;
              if (msg.a && msg.a.trim()) {
                html += ` <span style='color:#007700;'>A:</span> ${msg.a}`;
              }
              html += '</li>';
            }
            html += '</ul></div>';
            return html;
          }).join(''));
        var errEl = document.getElementById('shared-chat-error');
        if (errEl) errEl.style.display = 'none';
        if (typeof scrollShared === 'function') scrollShared();
      }).catch(e => {
        var errEl = document.getElementById('shared-chat-error');
        if (errEl) {
          errEl.textContent = 'Failed to load shared memory.';
          errEl.style.display = '';
        }
      });
    } catch (e) {
      var errEl = document.getElementById('shared-chat-error');
      if (errEl) {
        errEl.textContent = 'Failed to load shared memory.';
        errEl.style.display = '';
      }
    }
  }

  // --- Robust sync lock/debounce for private-to-shared memory sync ---
  let syncInProgress = false;
  let syncQueued = false;

  function uploadMissingPrivateToShared(force) {
    if (!sharedMemoryOnline && !force) return;
    if (syncInProgress) {
      syncQueued = true;
      return;
    }
    syncInProgress = true;
    getSharedChat().then(sharedArr => {
      const privateArr = getPrivateChat();
      const sharedKeys = new Set((sharedArr || []).map(msg => msg.ts + ':' + msg.q));
      const missing = privateArr.filter(msg => !sharedKeys.has(msg.ts + ':' + msg.q));      if (missing.length > 0) {
        const updatedArr = [...(sharedArr || []), ...missing.map(m => ({...m, user: m.user || userId || 'You'}))];
        setSharedChat(updatedArr).then(() => {
          renderSharedChat();
          populateMemorySectionTextareas(); // Refresh memory textboxes too!
          console.log('Synced', missing.length, 'private memories to shared memory');
          syncInProgress = false;
          if (syncQueued) {
            syncQueued = false;
            uploadMissingPrivateToShared();
          }
        });
      }else {
        syncInProgress = false;
        if (syncQueued) {
          syncQueued = false;
          uploadMissingPrivateToShared();
        }
      }
    }).catch(() => {
      syncInProgress = false;
      if (syncQueued) {
        syncQueued = false;
        uploadMissingPrivateToShared();
      }
    });
  }

  function getSharedChatWithSync() {
    return getSharedChat().then(arr => {
      if (sharedMemoryOnline) {
        uploadMissingPrivateToShared();
      }
      return arr;
    });
  }

  // --- Show user details in chat UI ---
  function fetchAndDisplayUserDetails() {
    if (!userId) return;
    fetch('/client-lookup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: userId })
    })
      .then(r => r.json())
      .then(data => {
        let details = '';
        if (data.status === 'ok' && data.record) {
          if (data.record.client_id) {
            details += `<b>Client ID:</b> ${data.record.client_id} `;
          }
          if (data.record.env_id) {
            details += `<b>Env ID:</b> ${data.record.env_id} `;
          }
        }
        if (details) {
          let infoDiv = document.getElementById('user-details');
          if (!infoDiv) {
            infoDiv = document.createElement('div');
            infoDiv.id = 'user-details';
            infoDiv.style = 'margin-bottom:12px;font-size:1em;color:#333;';
            chatSection.insertBefore(infoDiv, chatSection.firstChild);
          }
          infoDiv.innerHTML = details;
        }
      });
  }

  // On load, if authenticated, show user details
  if (userId) {
    fetchAndDisplayUserDetails();
  }
  // Also fetch details after authentication event
  window.addEventListener('storage', function(e) {
    if (e.key === USER_ID_KEY && e.newValue) {
      userId = e.newValue;
      fetchAndDisplayUserDetails();
    }
  });

  // --- Listen for email save on /client/<userId> and update chat userId if needed ---
  window.addEventListener('storage', function(e) {
    if (e.key === 'ici-client-email-' + userId && e.newValue) {
      // Email was saved for this userId; ensure chat userId is set and reload page for full details
      localStorage.setItem(USER_ID_KEY, userId);
      window.location.reload();
    }
  });

  // On chat load, always try to fetch and display user details (env id, client id, etc)
  function ensureUserDetails() {
    if (!userId) return;
    fetchAndDisplayUserDetails();
    fetch('/env-id').then(r => r.json()).then(d => {
      let infoDiv = document.getElementById('user-details');
      if (infoDiv && d.env_id) {
        if (!infoDiv.innerHTML.includes('Env ID')) {
          infoDiv.innerHTML += ` <b>Env ID:</b> ${d.env_id} `;
        }
      }
    });
  }

  if (userId) {
    ensureUserDetails();
  }

  // --- Message sending and handling ---
  chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const msg = chatInput.value.trim();
    if (!msg) return;
    chatInput.value = '';

    // --- Update private chat (localStorage) ---
    const privateChat = getPrivateChat();
    const newMsg = { q: msg, a: '', ts: Date.now(), user: userId || 'You' };
    privateChat.push(newMsg);
    setPrivateChat(privateChat);
    renderPrivateChat();

    // --- Update shared chat (server, running total) ---
    getSharedChat().then(sharedArr => {
      const updatedArr = [...sharedArr, {...newMsg, user: userId || 'Anonymous'}];
      setSharedChat(updatedArr).then(() => {
        renderSharedChat();
      });
    });

    // --- Send message to server for processing ---
    fetch('/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: msg, user_id: userId })
    })
      .then(r => r.json())
      .then(data => {
        if (data.answer) {
          // Update private chat with AI answer
          const privateChat = getPrivateChat();
          privateChat[privateChat.length - 1].a = data.answer;
          setPrivateChat(privateChat);
          renderPrivateChat();

          // Update shared chat with AI answer
          getSharedChat().then(sharedArr => {
            const aiMsg = { user: 'AI', q: msg, a: data.answer, ts: Date.now() };
            const updatedArr = [...sharedArr, aiMsg];
            setSharedChat(updatedArr).then(() => {
              renderSharedChat();
            });
          });
        }
      });
  });

  // --- Memory form handling ---
  const memoryForm = document.getElementById('memory-form');
  const memoryInput = document.getElementById('memory-input');
  const addToPrivateBtn = document.getElementById('add-to-private');
  const addToSharedBtn = document.getElementById('add-to-shared');
  const addToIpBtn = document.getElementById('add-to-ip');

  function addMemoryToPrivate(text) {
    const privateChat = getPrivateChat();
    const newMsg = { q: text, a: '', ts: Date.now(), user: userId || 'You' };
    privateChat.push(newMsg);
    setPrivateChat(privateChat);
    // Only update the private-box textarea, not all memory boxes
    const privateBox = document.getElementById('private-box');
    if (privateBox) {
      privateBox.value = formatMemoryDisplay(privateChat, 'private');
    }
    console.log('Added to private memory:', text);
  }

  function addMemoryToShared(text) {
    getSharedChat().then(sharedArr => {
      const newMsg = { q: text, a: '', ts: Date.now(), user: userId || 'Anonymous' };
      const updatedArr = [...sharedArr, newMsg];
      setSharedChat(updatedArr).then(() => {
        // Only update the shared (env-box) textarea, not all memory boxes
        const envBox = document.getElementById('env-box');
        if (envBox) {
          getSharedChat().then(messages => {
            envBox.value = formatMemoryDisplay(messages, 'shared');
          });
        }
        console.log('Added to shared memory:', text);
      });
    });
  }

  // Helper to get public IP (using a public API)
  function getPublicIP() {
    return fetch('https://api.ipify.org?format=json')
      .then(r => r.json())
      .then(data => data.ip)
      .catch(() => '');
  }

  function addMemoryToIp(text) {
    getPublicIP().then(function(publicIp) {
      fetch(`/client-box?env_id=ici-demo&public_ip=${encodeURIComponent(publicIp)}`)
        .then(r => r.json())
        .then(data => {
          const currentData = Array.isArray(data.value) ? data.value : [];
          const newMsg = { q: text, a: '', ts: Date.now(), user: userId || 'Anonymous' };
          const updatedArr = [...currentData, newMsg];
          return fetch('/client-box', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ env_id: 'ici-demo', public_ip: publicIp, value: updatedArr })
          });
        })
        .then(() => {
          // Only refresh the IP-shared textarea, not private
          const clientBox = document.getElementById('client-box');
          if (clientBox) {
            fetch(`/client-box?env_id=ici-demo&public_ip=${encodeURIComponent(publicIp)}`)
              .then(r => r.json())
              .then(data => {
                const messages = Array.isArray(data.value) ? data.value : [];
                clientBox.value = formatMemoryDisplay(messages, 'ip-shared');
              });
          }
          console.log('Added to IP-shared memory:', text);
        })
        .catch(err => {
          console.error('Failed to add to IP-shared memory:', err);
          alert('IP-shared memory is not available');
        });
    });
  }

  // Add event listeners for memory buttons
  if (addToPrivateBtn) {
    addToPrivateBtn.addEventListener('click', function() {
      const text = memoryInput.value.trim();
      if (!text) return;
      addMemoryToPrivate(text);
      memoryInput.value = '';
    });
  }

  if (addToSharedBtn) {
    addToSharedBtn.addEventListener('click', function() {
      const text = memoryInput.value.trim();
      if (!text) return;
      addMemoryToShared(text);
      memoryInput.value = '';
    });
  }

  if (addToIpBtn) {
    addToIpBtn.addEventListener('click', function() {
      const text = memoryInput.value.trim();
      if (!text) return;
      addMemoryToIp(text);
      memoryInput.value = '';
    });
  }
  // Also allow Enter key to add to shared memory by default
  if (memoryInput) {
    memoryInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        const text = memoryInput.value.trim();
        if (!text) return;
        addMemoryToShared(text);
        memoryInput.value = '';
      }
    });
  }  const debugTestSyncBtn = document.getElementById('debug-test-sync');
  const debugClearAllBtn = document.getElementById('debug-clear-all');
  const debugRefreshBtn = document.getElementById('debug-refresh');
  const debugTestApiBtn = document.getElementById('debug-test-api');
  
  if (debugTestSyncBtn) {
    debugTestSyncBtn.addEventListener('click', function() {
      // Add test private memories and trigger sync
      const testMessages = [
        { q: 'Test private memory 1', a: '', ts: Date.now() - 3000, user: userId || 'TestUser' },
        { q: 'Test private memory 2', a: '', ts: Date.now() - 2000, user: userId || 'TestUser' },
        { q: 'Test private memory 3', a: '', ts: Date.now() - 1000, user: userId || 'TestUser' }
      ];
      const privateArr = getPrivateChat();
      const updatedArr = [...privateArr, ...testMessages];
      setPrivateChat(updatedArr);
      populateMemorySectionTextareas();
      console.log('Added test private memories:', testMessages);
      
      // Trigger sync after a brief delay
      setTimeout(() => {
        console.log('Triggering sync...');
        uploadMissingPrivateToShared(true);
      }, 500);
    });
  }
  
  if (debugClearAllBtn) {
    debugClearAllBtn.addEventListener('click', function() {
      setPrivateChat([]);
      setSharedChat([]).then(() => {
        populateMemorySectionTextareas();
        console.log('Cleared all memories');
      });
    });
  }
    if (debugRefreshBtn) {
    debugRefreshBtn.addEventListener('click', function() {
      console.log('Manually refreshing memory display...');
      populateMemorySectionTextareas();
    });
  }
  
  if (debugTestApiBtn) {
    debugTestApiBtn.addEventListener('click', function() {
      console.log('Testing API call...');
      fetch('/env-box?env_id=ici-demo')
        .then(r => r.json())
        .then(data => {
          console.log('API response:', data);
          alert('API Response: ' + JSON.stringify(data, null, 2));
        })
        .catch(err => {
          console.error('API error:', err);
          alert('API Error: ' + err.message);
        });
    });
  }

  // --- Helper: merge private chat into shared chat (no duplicates) ---
  function mergePrivateToShared(privateArr, sharedArr) {
    const seen = new Set(sharedArr.map(msg => msg.ts + ':' + msg.q));
    for (const msg of privateArr) {
      const key = msg.ts + ':' + msg.q;
      if (!seen.has(key)) {
        sharedArr.push(msg);
        seen.add(key);
      }
    }
    return sharedArr;
  }
  let scrollShared = null, scrollPrivate = null;

  // --- Group and weave chat messages by user and minute ---
  function aggregateAndWeaveChats(arr) {
    if (!Array.isArray(arr)) return [];
    // Sort by timestamp ascending
    arr = arr.slice().sort((a, b) => (a.ts || 0) - (b.ts || 0));
    // Group by user and minute
    const groups = [];
    let lastUser = null, lastMinute = null, currentGroup = null;
    for (const msg of arr) {
      const user = msg.user || 'Unknown';
      const d = new Date(msg.ts || 0);
      const minute = d.getFullYear() + '-' + (d.getMonth()+1).toString().padStart(2,'0') + '-' + d.getDate().toString().padStart(2,'0') + ' ' + d.getHours().toString().padStart(2,'0') + ':' + d.getMinutes().toString().padStart(2,'0');
      if (!currentGroup || user !== lastUser || minute !== lastMinute) {
        currentGroup = { user, minute, messages: [] };
        groups.push(currentGroup);
        lastUser = user;
        lastMinute = minute;
      }
      currentGroup.messages.push(msg);
    }
    return groups;
  }

  // --- Auto-scroll logic for chat histories ---
  function setupAutoScroll(container) {
    let autoScroll = true;
    function scrollToBottom() {
      if (autoScroll) {
        container.scrollTop = container.scrollHeight;
      }
    }
    // On scroll, check if user is at the bottom
    container.addEventListener('scroll', function() {
      // Allow 2px leeway for rounding
      if (container.scrollTop + container.clientHeight >= container.scrollHeight - 2) {
        autoScroll = true;
      } else {
        autoScroll = false;
      }
    });
    // Expose a method to trigger scroll after render
    return scrollToBottom;
  }

  // --- Auto-scroll for memory-section textareas ---
  function setupTextareaAutoScroll(textarea) {
    let autoScroll = true;
    function scrollToBottom() {
      if (autoScroll) {
        textarea.scrollTop = textarea.scrollHeight;
      }
    }
    textarea.addEventListener('scroll', function() {
      if (textarea.scrollTop + textarea.clientHeight >= textarea.scrollHeight - 2) {
        autoScroll = true;
      } else {
        autoScroll = false;
      }
    });
    // Watch for value changes (polling, since value may be set programmatically)
    let lastValue = textarea.value;
    setInterval(() => {
      if (textarea.value !== lastValue) {
        lastValue = textarea.value;
        scrollToBottom();
      }
    }, 300);
  }
  // --- Offline/online logic for shared memory ---
  let sharedMemoryOnline = true;
  let lastSharedArr = [];
  let sharedChatBox = null;
  // --- Socket.IO for real-time shared memory updates ---
  if (window.io) {
    const socket = io();
    socket.on('shared_memory_updated', function(data) {
      // Optionally, check env_id matches if you want to filter
      renderSharedChat();
      populateMemorySectionTextareas(); // Also refresh memory textboxes
    });
  }
  // === CONSOLIDATED INITIALIZATION ===
  document.addEventListener('DOMContentLoaded', function() {
    var jsDebug = document.getElementById('js-init-debug');
    if (jsDebug) {
      jsDebug.style.display = '';
      jsDebug.textContent = 'JS loaded: DOMContentLoaded fired.';
    }
    // Always show memory section for demo (moved from earlier in the script)
    showMemorySection();
    if (jsDebug) jsDebug.textContent += ' showMemorySection() called.';
    
    // Setup auto-scroll for chat histories
    if (sharedChatHistory) scrollShared = setupAutoScroll(sharedChatHistory);
    if (privateChatHistory) scrollPrivate = setupAutoScroll(privateChatHistory);

    // Setup auto-scroll for memory-section textareas
    const envBox = document.getElementById('env-box');
    const clientBox = document.getElementById('client-box');
    const privateBox = document.getElementById('private-box');
    if (envBox) setupTextareaAutoScroll(envBox);
    if (clientBox) setupTextareaAutoScroll(clientBox);
    if (privateBox) setupTextareaAutoScroll(privateBox);

    // Populate memory textareas
    populateMemorySectionTextareas();

    // Initial render (must be after scrollPrivate/scrollShared are initialized)
    renderPrivateChat();
    if (typeof scrollPrivate === 'function') scrollPrivate();
    renderSharedChat();
    if (typeof scrollShared === 'function') scrollShared();    // Setup offline detection
    sharedChatBox = document.getElementById('shared-chat-history');

    function setSharedMemoryOfflineUI(isOffline) {
      if (!sharedChatBox) return;
      if (isOffline) {
        sharedChatBox.style.outline = '2px solid red';
        sharedChatBox.setAttribute('aria-label', 'Shared Memory Chat History (Offline)');
      } else {
        sharedChatBox.style.outline = '';
        sharedChatBox.setAttribute('aria-label', 'Shared Memory Chat History');
      }
    }

    function trySharedFetch(fn) {
      // Helper to wrap shared memory fetches and handle offline UI
      return fn().then(
        (result) => {
          if (!sharedMemoryOnline) {
            sharedMemoryOnline = true;
            setSharedMemoryOfflineUI(false);
          }
          return result;
        },
        (err) => {
          if (sharedMemoryOnline) {
            sharedMemoryOnline = false;
            setSharedMemoryOfflineUI(true);
          }
          return null;
        }
      );
    }

    // --- Get env_id from localStorage or fallback ---
    function getEnvId() {
      return 'ici-demo';
    }    // Listen for online/offline events
    window.addEventListener('online', function() {
      setTimeout(() => {
        getSharedChat().then(arr => {
          if (arr && arr.length > 0) {
            sharedMemoryOnline = true;
            setSharedMemoryOfflineUI(false);
            // Try to upload any missing private messages to shared
            uploadMissingPrivateToShared(true);
            // Refresh memory textboxes after going online
            populateMemorySectionTextareas();
          }
        });
      }, 1000);
    });
    window.addEventListener('offline', function() {
      sharedMemoryOnline = false;
      setSharedMemoryOfflineUI(true);
    });    // --- Debugging / manual control ---
    window.debugForceOnline = function() {
      sharedMemoryOnline = true;
      setSharedMemoryOfflineUI(false);
    }
    window.debugForceOffline = function() {
      sharedMemoryOnline = false;
      setSharedMemoryOfflineUI(true);
    }
    window.debugResharePrivateMemory = function() {
      const privateArr = getPrivateChat();
      setSharedChat([...privateArr]).then(renderSharedChat);
    }
    window.debugClearPrivateMemory = function() {
      setPrivateChat([]);
      renderPrivateChat();
      populateMemorySectionTextareas();
    }
    window.debugClearSharedMemory = function() {
      setSharedChat([]).then(renderSharedChat).then(() => populateMemorySectionTextareas());
    }
    window.debugShowPrivateMemory = function() {
      const privateArr = getPrivateChat();
      alert('Private Memory:\n' + JSON.stringify(privateArr, null, 2));
    }
    window.debugShowSharedMemory = function() {
      getSharedChat().then(arr => {
        alert('Shared Memory:\n' + JSON.stringify(arr, null, 2));
      });
    }
    window.debugAddTestPrivateMemories = function() {
      const testMessages = [
        { q: 'Test memory 1', a: '', ts: Date.now() - 3000, user: userId || 'TestUser' },
        { q: 'Test memory 2', a: '', ts: Date.now() - 2000, user: userId || 'TestUser' },
        { q: 'Test memory 3', a: '', ts: Date.now() - 1000, user: userId || 'TestUser' }
      ];
      const privateArr = getPrivateChat();
      const updatedArr = [...privateArr, ...testMessages];
      setPrivateChat(updatedArr);
      populateMemorySectionTextareas();
      console.log('Added test private memories:', testMessages);
    }
    window.debugTriggerSync = function() {
      console.log('Manually triggering sync...');
      uploadMissingPrivateToShared(true);
    }
      // Debug function to force refresh memory display
    window.debugRefreshMemory = function() {
      console.log('Manually refreshing memory display...');
      populateMemorySectionTextareas();
    }
    
    // Debug function to test elements
    window.debugTestElements = function() {
      const envBox = document.getElementById('env-box');
      const clientBox = document.getElementById('client-box');
      const privateBox = document.getElementById('private-box');
      console.log('Elements:', { envBox, clientBox, privateBox });
      console.log('Env box value:', envBox ? envBox.value : 'null');
    }

    // --- Service worker registration (for push notifications, etc) ---
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js').then(registration => {
        console.log('Service Worker registered with scope:', registration.scope);
      }).catch(error => {
        console.error('Service Worker registration failed:', error);
      });
    }

    // Ensure env_id exists in localStorage for this user
    (function ensureEnvId() {
      if (!localStorage.getItem('ici-env-id')) {
        // Generate a random env_id (10-char hex)
        const arr = new Uint8Array(8);
        window.crypto.getRandomValues(arr);
        const hex = Array.from(arr).map(b => b.toString(16).padStart(2, '0')).join('');
        localStorage.setItem('ici-env-id', hex);
      }
    })();
  });
});
  // === Auto-register client on page load (with public IP) ===
  function autoRegisterClient() {
    if (!userId) return;
    getPublicIP().then(function(publicIp) {
      fetch('/client-remember', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ client_id: userId, public_ip: publicIp })
      })
      .then(r => r.json())
      .then(data => {
        console.log('Auto-register client result:', data);
      })
      .catch(err => {
        console.warn('Auto-register client failed:', err);
      });
    });
  }
  // Call auto-register after DOMContentLoaded and userId is set
  document.addEventListener('DOMContentLoaded', function() {
    // ...existing code...
    autoRegisterClient();
    // ...existing code...
  });
// QR Code Auth UI Logic for Chat Page
function onQRCodeScanned(walletAddress, clientData) {
    // Hide QR code UI
    const qrSection = document.getElementById('qrSection');
    if (qrSection) qrSection.style.display = 'none';
    // Show client details UI (from client.html template)
    fetch('/client?wallet=' + encodeURIComponent(walletAddress))
        .then(res => res.text())
        .then(html => {
            const clientDetails = document.getElementById('clientDetails');
            if (clientDetails) {
                clientDetails.innerHTML = html;
                clientDetails.style.display = 'block';
            }
        });
    // Update chat memory logic to use walletAddress as the user_id
    window.currentUserId = walletAddress;
    // Optionally, trigger a UI notification
    if (window.showToast) window.showToast('Authenticated as client: ' + walletAddress);
}