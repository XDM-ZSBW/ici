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
  // Only show metadata, no email logic
  // Populate known data
  fetchEnvId().then(envId => { document.getElementById('info-env-id').textContent = envId; });
  fetchClientIp().then(ip => { document.getElementById('info-client-ip').textContent = ip; });
  fetchServerIp().then(ip => { document.getElementById('info-server-ip').textContent = ip; });
  document.getElementById('info-client-id').textContent = CLIENT_ID_VALUE;
  // Hide email field if present
  var emailBox = document.getElementById('email-box');
  if (emailBox) emailBox.style.display = 'none';
  var emailStatus = document.getElementById('email-status');
  if (emailStatus) emailStatus.style.display = 'none';
  var infoEmail = document.getElementById('info-email');
  if (infoEmail) infoEmail.style.display = 'none';
  var saveBtn = document.getElementById('save-email-btn');
  if (saveBtn) saveBtn.style.display = 'none';
});
