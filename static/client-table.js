// client-table rendering for client.html (bottom of page)
function renderClientTableOnClientPage(table) {
    const pre = document.getElementById('client-table-json');
    const tbl = document.getElementById('client-table-html');
    if (!pre || !tbl) return;
    pre.textContent = JSON.stringify(table, null, 2);
    if (!Array.isArray(table) || table.length === 0) {
        tbl.innerHTML = '<tr><td>No records</td></tr>';
        return;
    }
    const cols = Object.keys(table[0]);
    let html = '<tr>' + cols.map(c => `<th>${c}</th>`).join('') + '</tr>';
    for (const row of table) {
        html += '<tr>' + cols.map(c => `<td>${row[c] !== undefined ? row[c] : ''}</td>`).join('') + '</tr>';
    }
    tbl.innerHTML = html;
}

document.addEventListener('DOMContentLoaded', function() {
    // ...existing code for client page...
    // At the end, render the client table at the bottom
    fetch('/client-table').then(r => r.json()).then(renderClientTableOnClientPage);
});
