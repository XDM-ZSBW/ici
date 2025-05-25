// index.js
// For the landing page: fetch and render README.md as HTML

document.addEventListener('DOMContentLoaded', function() {
  const readmeDiv = document.getElementById('readme-content');
  if (!readmeDiv) return;

  fetch('/readme')
    .then(r => r.ok ? r.text() : Promise.reject('Failed to load README'))
    .then(md => {
      // Simple markdown to HTML converter for headings, bold, italics, and lists
      function mdToHtml(md) {
        let html = md;
        // Headings
        html = html.replace(/^###### (.*)$/gm, '<h6>$1</h6>');
        html = html.replace(/^##### (.*)$/gm, '<h5>$1</h5>');
        html = html.replace(/^#### (.*)$/gm, '<h4>$1</h4>');
        html = html.replace(/^### (.*)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.*)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.*)$/gm, '<h1>$1</h1>');
        // Bold **text** or __text__
        html = html.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>');
        html = html.replace(/__(.*?)__/g, '<b>$1</b>');
        // Italic *text* or _text_
        html = html.replace(/\*(.*?)\*/g, '<i>$1</i>');
        html = html.replace(/_(.*?)_/g, '<i>$1</i>');
        // Unordered lists
        html = html.replace(/(^|\n)[ ]*\-[ ](.*?)(?=\n|$)/g, '$1<li>$2</li>');
        html = html.replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
        // Ordered lists
        html = html.replace(/(^|\n)[ ]*\d+\.[ ](.*?)(?=\n|$)/g, '$1<ol><li>$2</li></ol>');
        // Paragraphs (very basic, skip if already block)
        html = html.replace(/(^|\n)(?!<h\d|<ul>|<ol>|<li>|<pre>|<\/)([^\n<][^\n]*)/g, '$1<p>$2</p>');
        // Code blocks (triple backticks)
        html = html.replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        // Remove multiple <ul> wrappers
        html = html.replace(/(<\/ul>)(\s*)<ul>/g, '');
        // Remove multiple <ol> wrappers
        html = html.replace(/(<\/ol>)(\s*)<ol>/g, '');
        return html;
      }
      readmeDiv.innerHTML = mdToHtml(md);
    })
    .catch(() => {
      readmeDiv.textContent = 'Could not load README.';
    });
});
