// client.js
// Sets the client-id value from the template variable

function fetchEnvId() {
  return fetch('/env-id').then(r => r.json()).then(d => d.env_id).catch(() => 'unknown-env-id');
}
function fetchClientIp() {
  return fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(() => 'unknown-ip');
}
function fetchServerIp() {
  return fetch('/data').then(r => r.json()).then(d => d.key || 'unknown-server-ip').catch(() => 'unknown-server-ip');
}

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('client-id-value').textContent = CLIENT_ID_VALUE;

  const emailBox = document.getElementById('email-box');
  const emailStatus = document.getElementById('email-status');
  const infoEnvId = document.getElementById('info-env-id');
  const infoClientIp = document.getElementById('info-client-ip');
  const infoServerIp = document.getElementById('info-server-ip');
  const infoClientId = document.getElementById('info-client-id');
  const infoEmail = document.getElementById('info-email');

  // Restore last valid email from localStorage if present, or from server if provided
  const EMAIL_STORAGE_KEY = 'ici-client-email-' + CLIENT_ID_VALUE;
  let lastEmail = '';
  if (window.SERVER_EMAIL_VALUE && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(window.SERVER_EMAIL_VALUE)) {
    lastEmail = window.SERVER_EMAIL_VALUE;
    emailBox.value = lastEmail;
    infoEmail.textContent = lastEmail;
    localStorage.setItem(EMAIL_STORAGE_KEY, lastEmail);
    lookupClient(CLIENT_ID_VALUE);
  } else {
    lastEmail = localStorage.getItem(EMAIL_STORAGE_KEY) || '';
    if (lastEmail && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(lastEmail)) {
      emailBox.value = lastEmail;
      infoEmail.textContent = lastEmail;
      lookupClient(CLIENT_ID_VALUE);
    } else {
      lookupClient(CLIENT_ID_VALUE);
    }
  }

  function isValidEmail(email) {
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  }

  function saveEmail(email) {
    if (!isValidEmail(email)) return; // Prevent submission of invalid/incomplete emails
    fetch('/client-remember', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email,
        client_id: CLIENT_ID_VALUE
      })
    }).then(r => r.json()).then(data => {
      emailStatus.textContent = 'Saved!';
      emailStatus.style.color = '#007700';
      infoEmail.textContent = email;
      localStorage.setItem(EMAIL_STORAGE_KEY, email);
    }).catch(() => {
      emailStatus.textContent = 'Error saving email.';
      emailStatus.style.color = '#bb0000';
    });
  }

  let isEditingEmail = false;
  emailBox.addEventListener('focus', function() { isEditingEmail = true; });
  emailBox.addEventListener('blur', function() { isEditingEmail = false; });

  function lookupClient(clientId) {
    fetch('/client-lookup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ client_id: clientId })
    }).then(r => r.json()).then(data => {
      if (data.status === 'ok' && data.record) {
        if (data.record.email) {
          // Only update the textbox if not editing or value is different
          if (!isEditingEmail && emailBox.value !== data.record.email) {
            emailBox.value = data.record.email;
          }
          infoEmail.textContent = data.record.email;
          localStorage.setItem(EMAIL_STORAGE_KEY, data.record.email);
        } else {
          if (!isEditingEmail) {
            emailBox.value = '';
          }
          infoEmail.textContent = '';
          localStorage.removeItem(EMAIL_STORAGE_KEY);
        }
      }
    });
  }

  // Helper: check if clientId matches a record in memory (localStorage or server)
  function hasMemoryForClient(clientId) {
    // Check localStorage for a valid email for this clientId
    const key = 'ici-client-email-' + clientId;
    const email = localStorage.getItem(key);
    return email && isValidEmail(email);
  }

  // On page load, always show metadata, but only display memory if the URL matches a record in memory
  fetchEnvId().then(envId => { infoEnvId.textContent = envId; });
  fetchClientIp().then(ip => { infoClientIp.textContent = ip; });
  fetchServerIp().then(ip => { infoServerIp.textContent = ip; });
  infoClientId.textContent = CLIENT_ID_VALUE;

  function enableEmailInput() {
    emailBox.disabled = false;
    document.getElementById('save-email-btn').disabled = false;
  }
  function disableEmailInput() {
    emailBox.disabled = true;
    document.getElementById('save-email-btn').disabled = true;
  }

  function displayMemoryIfMatch(clientId) {
    if (hasMemoryForClient(clientId)) {
      // Show memory as usual
      lookupClient(clientId);
      enableEmailInput();
    } else {
      // No memory: clear display and disable input, but always show metadata
      emailBox.value = '';
      infoEmail.textContent = '';
      emailStatus.textContent = '';
      disableEmailInput();
    }
  }

  displayMemoryIfMatch(CLIENT_ID_VALUE);

  // Only save on button click
  document.getElementById('save-email-btn').addEventListener('click', function(e) {
    e.preventDefault();
    const email = emailBox.value.trim();
    if (isValidEmail(email)) {
      saveEmail(email);
      emailStatus.textContent = 'Valid email';
      emailStatus.style.color = '#007700';
      infoEmail.textContent = email;
      localStorage.setItem(EMAIL_STORAGE_KEY, email);
      enableEmailInput(); // Re-enable input after save
    } else {
      emailStatus.textContent = 'Invalid email';
      emailStatus.style.color = '#bb0000';
      infoEmail.textContent = '';
      localStorage.removeItem(EMAIL_STORAGE_KEY);
      disableEmailInput();
    }
  });
});
