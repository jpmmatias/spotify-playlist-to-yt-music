async function authenticateYouTubeMusic() {
    const headersInput = document.getElementById('youtube-headers');
    const statusDiv = document.getElementById('auth-status');
    const headers_raw = headersInput.value.trim();

    // Reset status
    statusDiv.innerHTML = '';
    statusDiv.className = '';

    // Basic validation
    if (!headers_raw) {
        showError('Please paste the cURL command from YouTube Music');
        return;
    }

    // Check if it's a cURL command
    if (!headers_raw.toLowerCase().startsWith('curl')) {
        showError('Please copy the full cURL command from the Network tab');
        return;
    }

    // Check for required headers
    const requiredHeaders = ['cookie:', 'x-goog-authuser:'];
    const missingHeaders = requiredHeaders.filter(header => 
        !headers_raw.toLowerCase().includes(header)
    );

    if (missingHeaders.length > 0) {
        showError(`Missing required headers: ${missingHeaders.join(', ')}<br>
                  Please make sure to copy the full cURL command from a "browse" request.`);
        return;
    }

    try {
        statusDiv.innerHTML = 'Authenticating...';
        statusDiv.className = 'info';

        const response = await fetch('/youtube/auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ headers_raw })
        });

        const data = await response.json();
        
        if (response.ok) {
            showSuccess('YouTube Music authenticated successfully!');
        } else {
            showError(`Authentication failed: ${data.message}`);
        }
    } catch (error) {
        showError('Error authenticating with YouTube Music: ' + error);
    }
}

function showError(message) {
    const statusDiv = document.getElementById('auth-status');
    statusDiv.innerHTML = `❌ ${message}`;
    statusDiv.className = 'error';
}

function showSuccess(message) {
    const statusDiv = document.getElementById('auth-status');
    statusDiv.innerHTML = `✅ ${message}`;
    statusDiv.className = 'success';
}

// Add this CSS to your stylesheet
const style = document.createElement('style');
style.textContent = `
    #auth-status {
        margin-top: 10px;
        padding: 10px;
        border-radius: 4px;
    }
    #auth-status.error {
        background-color: #ffe6e6;
        color: #dc3545;
        border: 1px solid #dc3545;
    }
    #auth-status.success {
        background-color: #e6ffe6;
        color: #28a745;
        border: 1px solid #28a745;
    }
    #auth-status.info {
        background-color: #e6f3ff;
        color: #0056b3;
        border: 1px solid #0056b3;
    }
`;
document.head.appendChild(style);