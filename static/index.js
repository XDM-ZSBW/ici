// index.js
// For the landing page: fetch and render README.md as HTML

document.addEventListener('DOMContentLoaded', function() {
  const readmeDiv = document.getElementById('readme-content');
  if (!readmeDiv) return;

  fetch('/readme')
    .then(r => r.ok ? r.text() : Promise.reject('Failed to load README'))
    .then(md => {
      // Use GitHub's API or a CDN for markdown rendering, or a simple client-side converter
      // For now, use a basic converter for demo (show as <pre> if no converter)
      if (window.marked) {
        readmeDiv.innerHTML = window.marked.parse(md);
      } else {
        // fallback: preformatted
        readmeDiv.innerHTML = '<pre style="white-space:pre-wrap">' + md.replace(/[<>&]/g, c => ({'<':'&lt;','>':'&gt;','&':'&amp;'}[c])) + '</pre>';
      }
    })
    .catch(() => {
      readmeDiv.textContent = 'Could not load README.';
    });
});
