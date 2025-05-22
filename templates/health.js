const health = (req, res) => {
  res.status(200).json({
    status: 'UP',
    timestamp: new Date().toISOString(),
  });
};

// Function to fetch health status from the server
async function fetchHealthStatus() {
    try {
        const response = await fetch('/health');
        const data = await response.json();

        // Update the health status on the page
        document.getElementById('health-status').textContent = data.status;
    } catch (error) {
        console.error('Error fetching health status:', error);
        document.getElementById('health-status').textContent = 'Error: Could not retrieve health status.';
    }
}

// Fetch health status initially
fetchHealthStatus();

// Fetch health status every 5 seconds (adjust as needed)
//setInterval(fetchHealthStatus, 5000);

module.exports = {
  health,
};
