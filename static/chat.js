// chat.js
// ICI Chat: Shared (server) and private (localStorage) memory chat

document.addEventListener('DOMContentLoaded', function() {
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

  function showMemorySection() {
    document.getElementById('chat-section').style.display = 'none';
    document.getElementById('memory-section').style.display = '';
  }
  function showChatSection() {
    document.getElementById('memory-section').style.display = 'none';
    document.getElementById('chat-section').style.display = '';
  }

  // Check authentication
  if (!userId) {
    showAuthPrompt();
  } else if (localStorage.getItem(AUTH_VIA_QR_KEY) === '1') {
    showMemorySection();
  } else {
    showChatSection();
  }

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
    } catch (e) {
      var errEl = document.getElementById('private-chat-error');
      if (errEl) {
        errEl.textContent = 'Failed to load private memory.';
        errEl.style.display = '';
      }
    }
  }

  // Shared chat via server
  function getSharedChat() {
    return fetch('/env-box', { method: 'GET' })
      .then(r => r.json())
      .then(data => Array.isArray(data.value) ? data.value : [])
      .catch(() => []);
  }
  function setSharedChat(arr) {
    // Always POST the full array (running total)
    // Ensure every message has a user field
    const arrWithUser = arr.map(msg => ({...msg, user: msg.user || userId || 'Anonymous'}));
    return fetch('/env-box', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: arrWithUser })
    });
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
      const missing = privateArr.filter(msg => !sharedKeys.has(msg.ts + ':' + msg.q));
      if (missing.length > 0) {
        const updatedArr = [...(sharedArr || []), ...missing.map(m => ({...m, user: m.user || userId || 'You'}))];
        setSharedChat(updatedArr).then(() => {
          renderSharedChat();
          syncInProgress = false;
          if (syncQueued) {
            syncQueued = false;
            uploadMissingPrivateToShared();
          }
        });
      } else {
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

  // --- Initial render
  renderPrivateChat();
  renderSharedChat();

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

  function renderSharedChat() {
    getSharedChatWithSync().then(arr => {
      // Always show the title, even if arr is empty or null
      let html = '<b>Shared Memory (Grouped by User & Minute)</b><br>';
      const groups = aggregateAndWeaveChats(arr || []);
      if (groups.length === 0) {
        html += '<span style="color:#888;">No shared memory yet.</span>';
      } else {
        html += groups.map(group => {
          let ghtml = `<div class=\"chat-group\"><span style='font-weight:bold;color:#2a5298;'>${group.user}</span> <span style='color:#888;'>[${group.minute}]</span><ul style='margin:0 0 8px 18px;padding:0;'>`;
          for (const msg of group.messages) {
            ghtml += `<li><span style='color:#333;'>Q:</span> ${msg.q}`;
            if (msg.a && msg.a.trim()) {
              ghtml += ` <span style='color:#007700;'>A:</span> ${msg.a}`;
            }
            ghtml += '</li>';
          }
          ghtml += '</ul></div>';
          return ghtml;
        }).join('');
      }
      if (sharedChatHistory) sharedChatHistory.innerHTML = html;
      var errEl = document.getElementById('shared-chat-error');
      if (errEl) errEl.style.display = 'none';
    }).catch(e => {
      var errEl = document.getElementById('shared-chat-error');
      if (errEl) {
        errEl.textContent = 'Failed to load shared memory.';
        errEl.style.display = '';
      }
    });
  }

  // --- Socket.IO for real-time shared memory updates ---
  if (window.io) {
    const socket = io();
    socket.on('shared_memory_updated', function(data) {
      // Optionally, check env_id matches if you want to filter
      renderSharedChat();
    });
  }

  // --- Offline/online logic for shared memory ---
  let sharedMemoryOnline = true;
  let lastSharedArr = [];
  let sharedChatBox = null;
  document.addEventListener('DOMContentLoaded', function() {
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
    }

    // Patch getSharedChat and setSharedChat to send env_id
    function getSharedChat() {
      const envId = getEnvId();
      return trySharedFetch(() => fetch('/env-box' + (envId ? ('?env_id=' + encodeURIComponent(envId)) : ''), { method: 'GET' })
        .then(r => r.json())
        .then(data => Array.isArray(data.value) ? data.value : []));
    }
    function setSharedChat(arr) {
      if (!sharedMemoryOnline) return Promise.resolve(); // Don't try to update if offline
      const arrWithUser = arr.map(msg => ({...msg, user: msg.user || userId || 'Anonymous'}));
      const envId = getEnvId();
      return trySharedFetch(() => fetch('/env-box' + (envId ? ('?env_id=' + encodeURIComponent(envId)) : ''), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value: arrWithUser, env_id: envId })
      }));
    }

    // --- After any successful shared memory fetch, if we were previously offline, sync private to shared ---
    function getSharedChatWithSync() {
      return getSharedChat().then(arr => {
        if (sharedMemoryOnline) {
          uploadMissingPrivateToShared();
        }
        return arr;
      });
    }

    // --- Message sending and handling (patch for offline) ---
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
      if (sharedMemoryOnline) {
        getSharedChat().then(sharedArr => {
          const updatedArr = [...sharedArr, {...newMsg, user: userId || 'Anonymous'}];
          setSharedChat(updatedArr).then(() => {
            renderSharedChat();
          });
        });
      } // else: skip shared memory update

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
            if (sharedMemoryOnline) {
              getSharedChat().then(sharedArr => {
                const aiMsg = { user: 'AI', q: msg, a: data.answer, ts: Date.now() };
                const updatedArr = [...sharedArr, aiMsg];
                setSharedChat(updatedArr).then(() => {
                  renderSharedChat();
                });
              });
            }
          }
        });
    });

    // Listen for online/offline events
    window.addEventListener('online', function() {
      setTimeout(() => {
        getSharedChat().then(arr => {
          if (arr && arr.length > 0) {
            sharedMemoryOnline = true;
            setSharedMemoryOfflineUI(false);
            // Try to upload any missing private messages to shared
            uploadMissingPrivateToShared(true);
          }
        });
      }, 1000);
    });
    window.addEventListener('offline', function() {
      sharedMemoryOnline = false;
      setSharedMemoryOfflineUI(true);
    });

    // --- Debugging / manual control ---
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
    }
    window.debugClearSharedMemory = function() {
      setSharedChat([]).then(renderSharedChat);
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