// Function to fetch data from the server
async function fetchData() {
  try {
    const response = await fetch('/data'); // Replace '/data' with your actual endpoint
    const data = await response.text(); // Or response.json() if your server sends JSON

    // Update the content on the page
    document.getElementById('content-area').textContent = data;
  } catch (error) {
    console.error('Error fetching data:', error);
    document.getElementById('content-area').textContent = 'Error: Could not retrieve data.';
  }
}

// Fetch data initially
fetchData();

// Fetch data every 5 seconds (adjust as needed)
// setInterval(fetchData, 10000);