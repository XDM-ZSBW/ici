// join.js
// Generates a QR code for /join/<client-id> on this domain

// Helper: Generate client ID (same as in main app)
function getPrivateClientId(envId, publicIp) {
    const info = `${envId}|${publicIp}|${navigator.userAgent}`;
    return btoa(info).slice(0, 16);
}

function fetchEnvId() {
    if (window.env_id_from_server) return Promise.resolve(window.env_id_from_server);
    return fetch('/env-id').then(r => r.json()).then(d => d.env_id).catch(() => 'unknown-env-id');
}
function fetchPublicIp() {
    return fetch('https://api.ipify.org?format=json').then(r => r.json()).then(d => d.ip).catch(() => 'unknown-ip');
}

function makeQrCode(text, canvas) {
    // Use a minimal QR code generator (no dependencies)
    // For production, use a library like QRCode.js
    // Here, use a CDN for QRCode.js for simplicity
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/qrious/4.0.2/qrious.min.js';
    script.onload = function() {
        const qr = new QRious({
            element: canvas,
            value: text,
            size: 256,
            level: 'H'
        });
    };
    document.body.appendChild(script);
}

document.addEventListener('DOMContentLoaded', function() {
    Promise.all([fetchEnvId(), fetchPublicIp()]).then(([envId, publicIp]) => {
        // Generate full 256-bit private-id (SHA-256 hex of info string)
        const info = `${envId}|${publicIp}|${navigator.userAgent}`;
        function setQrWithPrivateId(pid) {
            const baseUrl = window.location.origin;
            const clientUrl = `${baseUrl}/client/${pid}`;
            document.getElementById('qr-url').textContent = clientUrl;
            makeQrCode(clientUrl, document.getElementById('qr-code'));
        }
        if (window.crypto && window.crypto.subtle && window.TextEncoder) {
            window.crypto.subtle.digest('SHA-256', new TextEncoder().encode(info)).then(buf => {
                const pid = Array.from(new Uint8Array(buf)).map(b => b.toString(16).padStart(2, '0')).join('');
                setQrWithPrivateId(pid);
            });
        } else {
            // Fallback: use btoa (not cryptographically strong, but always available)
            const pid = btoa(info).split('').map(c => c.charCodeAt(0).toString(16).padStart(2, '0')).join('').slice(0, 64);
            setQrWithPrivateId(pid);
        }
    });
});
