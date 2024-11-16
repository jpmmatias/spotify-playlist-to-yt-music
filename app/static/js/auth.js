// Authentication related functionality
const auth = {
    youtube: {
        authenticate: async function() {
            try {
                console.log("[Debug] Starting YouTube OAuth authentication");
                const authButton = document.getElementById('auth-button-main');
                const authStatus = document.getElementById('auth-status-main');
                
                authButton.disabled = true;
                authStatus.textContent = 'Starting OAuth flow...';
                
                const response = await fetch('/youtube/auth', {
                    method: 'POST'
                });

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.message || 'Authentication failed');
                }

                authStatus.textContent = 'Authentication successful!';
                authStatus.className = 'mt-2 text-sm text-green-600';
                
                // Hide the auth section
                const authSection = document.querySelector('.youtube-auth-section');
                if (authSection) {
                    authSection.style.display = 'none';
                }

                return true;

            } catch (error) {
                console.error("[Debug] Authentication error:", error);
                throw error;
            }
        },

        // Add the checkAuth function
        checkAuth: async function() {
            try {
                const response = await fetch('/youtube/check-auth', {
                    method: 'GET',
                    credentials: 'include'
                });

                if (!response.ok) {
                    return false;
                }

                const data = await response.json();
                return data.authenticated === true;

            } catch (error) {
                console.error("[Debug] Auth check error:", error);
                return false;
            }
        }
    }
};

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    const authButton = document.getElementById('auth-button-main');
    const authStatus = document.getElementById('auth-status-main');

    if (authButton) {
        authButton.addEventListener('click', async () => {
            try {
                authStatus.textContent = 'Authenticating...';
                authButton.disabled = true;

                await auth.youtube.authenticate();
                
                authStatus.textContent = 'Authentication successful!';
                authStatus.className = 'mt-2 text-sm text-green-600';
                
                // Hide the auth section after success
                const authSection = document.querySelector('.youtube-auth-section');
                if (authSection) {
                    authSection.style.display = 'none';
                }

            } catch (error) {
                console.error('Auth error:', error);
                authStatus.textContent = `Authentication failed: ${error.message}`;
                authStatus.className = 'mt-2 text-sm text-red-600';
                authButton.disabled = false;
            }
        });
    }
}); 