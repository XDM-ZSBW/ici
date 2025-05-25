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

  // Populate known data
  fetchEnvId().then(envId => { infoEnvId.textContent = envId; });
  fetchClientIp().then(ip => { infoClientIp.textContent = ip; });
  // For demo, use /data endpoint as a placeholder for server IP (replace with real server IP in production)
  fetchServerIp().then(ip => { infoServerIp.textContent = ip; });
  infoClientId.textContent = CLIENT_ID_VALUE;
  infoEmail.textContent = '';

  function isValidEmail(email) {
    return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email);
  }

  function saveEmail(email) {
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
    }).catch(() => {
      emailStatus.textContent = 'Error saving email.';
      emailStatus.style.color = '#bb0000';
    });
  }

  function lookupClient(email, clientId) {
    return fetch('/client-lookup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email, client_id: clientId })
    }).then(r => r.json()).then(data => {
      if (data.status === 'ok' && data.record) {
        // Display the last known record (could be extended to show more fields)
        document.getElementById('client-id-value').textContent = data.record.client_id;
        infoEmail.textContent = data.record.email;
        // Optionally, show a message or restore more data here
      }
    });
  }

  // On page load, try to look up by client_id (and by email if present in localStorage)
  lookupClient('', CLIENT_ID_VALUE);

  emailBox.addEventListener('input', function() {
    const email = emailBox.value.trim();
    if (isValidEmail(email)) {
      emailStatus.textContent = 'Valid email';
      emailStatus.style.color = '#007700';
      saveEmail(email);
      infoEmail.textContent = email;
      lookupClient(email, CLIENT_ID_VALUE);
    } else if (email.length > 0) {
      emailStatus.textContent = 'Invalid email';
      emailStatus.style.color = '#bb0000';
      infoEmail.textContent = '';
    } else {
      emailStatus.textContent = '';
      infoEmail.textContent = '';
    }
  });
});
