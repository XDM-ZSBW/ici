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
    // At the end, render the client table at the bottom, with auto-restore if needed
    function tryRenderOrRestoreClientTable() {
        fetch('/client-table').then(r => r.json()).then(function(table) {
            if ((!Array.isArray(table) || table.length === 0) && localStorage.getItem('ici-client-table-backup')) {
                const backup = localStorage.getItem('ici-client-table-backup');
                try {
                    const parsed = JSON.parse(backup);
                    if (Array.isArray(parsed) && parsed.length > 0) {
                        // Render backup immediately for user feedback
                        renderClientTableOnClientPage(parsed);
                        // POST to /client-table-restore
                        fetch('/client-table-restore', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: backup
                        }).then(r => r.json()).then(resp => {
                            if (resp.status === 'ok') {
                                setTimeout(tryRenderOrRestoreClientTable, 500);
                            }
                        });
                        return;
                    }
                } catch (e) { /* ignore */ }
            }
            renderClientTableOnClientPage(table);
        });
    }
    tryRenderOrRestoreClientTable();
});
