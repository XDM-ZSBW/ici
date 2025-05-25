// client.js
// Sets the client-id value from the template variable

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('client-id-value').textContent = CLIENT_ID_VALUE;

  const emailBox = document.getElementById('email-box');
  const emailStatus = document.getElementById('email-status');

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
    }).catch(() => {
      emailStatus.textContent = 'Error saving email.';
      emailStatus.style.color = '#bb0000';
    });
  }

  emailBox.addEventListener('input', function() {
    const email = emailBox.value.trim();
    if (isValidEmail(email)) {
      emailStatus.textContent = 'Valid email';
      emailStatus.style.color = '#007700';
      saveEmail(email);
    } else if (email.length > 0) {
      emailStatus.textContent = 'Invalid email';
      emailStatus.style.color = '#bb0000';
    } else {
      emailStatus.textContent = '';
    }
  });
});
