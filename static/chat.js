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
  function renderSharedChat() {
    getSharedChat().then(arr => {
      // Use aggregation and weaving for display
      const groups = aggregateAndWeaveChats(arr);
      sharedChatHistory.innerHTML = '<b>Shared Memory (Grouped by User & Minute)</b><br>' +
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
        }).join('');
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

  // Helper: merge private chat into shared chat (no duplicates)
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

  // On load, if shared memory is empty, reshare private memory
  function ensureSharedMemory() {
    getSharedChat().then(sharedArr => {
      const privateArr = getPrivateChat();
      if ((!sharedArr || sharedArr.length === 0) && privateArr.length > 0) {
        // Shared memory lost, reshare private memory
        setSharedChat([...privateArr]).then(renderSharedChat);
      } else if (privateArr.length > 0) {
        // Ensure shared memory is a running total of all private chats
        const merged = mergePrivateToShared(privateArr, sharedArr || []);
        if (merged.length !== sharedArr.length) {
          setSharedChat(merged).then(renderSharedChat);
        }
      }
    });
  }

  // Call on load
  ensureSharedMemory();

  // Initial render
  renderPrivateChat();
  renderSharedChat();

  // --- Socket.IO for real-time shared memory updates ---
  if (window.io) {
    const socket = io();
    socket.on('shared_memory_updated', function(data) {
      // Optionally, check env_id matches if you want to filter
      renderSharedChat();
    });
  }

  // Utility: Aggregate chat messages by user and minute, weave by time
  function aggregateAndWeaveChats(messages) {
    // messages: array of {user, q, a, ts}
    // 1. Group by user and minute
    const grouped = {};
    for (const msg of messages) {
        if (!msg.user || !msg.ts) continue;
        const date = new Date(msg.ts);
        const minuteKey = `${msg.user}|${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()} ${date.getHours()}:${date.getMinutes()}`;
        if (!grouped[minuteKey]) grouped[minuteKey] = [];
        grouped[minuteKey].push(msg);
    }
    // 2. Flatten to array, sort by earliest ts in each group
    const groups = Object.entries(grouped).map(([key, arr]) => ({
        user: arr[0].user,
        minute: key.split('|')[1],
        messages: arr,
        earliest: Math.min(...arr.map(m => m.ts))
    }));
    groups.sort((a, b) => a.earliest - b.earliest);
    // 3. Weave: interleave groups by time
    return groups;
}
});
