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
    privateChatHistory.innerHTML = '<b>Private Memory</b><br>' + arr.map(msg => `<div class="chat-message private"><b>You:</b> ${msg.q}<br><b>Memory:</b> ${msg.a}</div>`).join('');
  }

  // Shared chat via server
  function getSharedChat() {
    return fetch('/env-box', { method: 'GET' })
      .then(r => r.json())
      .then(data => Array.isArray(data.value) ? data.value : [])
      .catch(() => []);
  }
  function setSharedChat(arr) {
    return fetch('/env-box', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ value: arr })
    });
  }
  function renderSharedChat() {
    getSharedChat().then(arr => {
      sharedChatHistory.innerHTML = '<b>Shared Memory</b><br>' + arr.map(msg => `<div class="chat-message shared"><b>${msg.user||'User'}:</b> ${msg.q}<br><b>Memory:</b> ${msg.a}</div>`).join('');
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
          if (data.record.email) {
            details += `<b>Email:</b> ${data.record.email} `;
          }
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
    privateChat.push({ q: msg, a: '', ts: Date.now() });
    setPrivateChat(privateChat);
    renderPrivateChat();

    // --- Update shared chat (server) ---
    const sharedMsg = { user: '', q: msg, a: '', ts: Date.now() };
    setSharedChat([sharedMsg]).then(() => {
      // Refresh shared chat display
      renderSharedChat();
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
          const sharedMsg = { user: 'AI', q: msg, a: data.answer, ts: Date.now() };
          setSharedChat([sharedMsg]).then(() => {
            // Refresh shared chat display
            renderSharedChat();
          });
        }
      });
  });

  // Initial render
  renderPrivateChat();
  renderSharedChat();
});
