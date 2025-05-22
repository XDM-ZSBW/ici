// Function to fetch data from the server
async function fetchData() {
  try {
    const response = await fetch('/data'); // Replace '/data' with your actual endpoint
    const data = await response.json(); // Or response.text() if your server sends plain text

    // Update the content on the page
    document.getElementById('app-description').textContent = 'This app is designed to demonstrate continuous integration and deployment with Google Cloud Run.';
    document.getElementById('data-from-server').textContent = 'Data from server: ' + data.random_string; // Access the random_string property
  } catch (error) {
    console.error('Error fetching data:', error);
    document.getElementById('data-from-server').textContent = 'Error: Could not retrieve data.';
  }
}

// Fetch data initially
fetchData();

// Fetch data every 5 seconds (adjust as needed)
setInterval(fetchData, 5000);