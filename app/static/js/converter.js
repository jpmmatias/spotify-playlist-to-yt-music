// Playlist conversion functionality
const converter = {
    activeConversion: null,

    async convert(playlistId) {
        if (this.activeConversion) {
            ui.showToast('Another conversion is in progress', 'warning');
            return;
        }

        try {
            this.activeConversion = playlistId;
            const isAuthenticated = await auth.youtube.checkAuth();
            
            if (!isAuthenticated) {
                ui.showYouTubeAuthModal();
                return;
            }

            const button = document.querySelector(`button[data-playlist-id="${playlistId}"]`);
            const loadingSpinner = button.querySelector('.loading');
            const buttonText = button.querySelector('.text');
            
            // Update UI state
            button.disabled = true;
            loadingSpinner.classList.remove('hidden');
            buttonText.textContent = 'Starting...';

            const eventSource = new EventSource(`/convert/${playlistId}`, {
                withCredentials: true
            });

            this.setupEventHandlers(eventSource, playlistId);

        } catch (error) {
            console.error('Conversion error:', error);
            this.handleError(error);
        }
    },

    setupEventHandlers(eventSource, playlistId) {
        const button = document.querySelector(`button[data-playlist-id="${playlistId}"]`);
        const progressInfo = button.closest('.flex').querySelector('.progress-info');
        const loadingSpinner = button.querySelector('.loading');
        const buttonText = button.querySelector('.text');

        eventSource.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateProgress(data, button, buttonText, progressInfo);
        };

        eventSource.onerror = (error) => {
            this.handleError(error, button, buttonText, progressInfo, loadingSpinner);
            eventSource.close();
        };
    },

    updateProgress(data, button, buttonText, progressInfo) {
        progressInfo.classList.remove('hidden');
        if (data.status === 'progress') {
            buttonText.textContent = `Converting (${data.percentage}%)`;
            progressInfo.textContent = `Processing: ${data.track_name}`;
        } else if (data.status === 'complete') {
            buttonText.textContent = `Converted ${data.songs_found}/${data.total_tracks}`;
            progressInfo.textContent = 'Conversion complete!';
            button.classList.remove('bg-blue-500', 'hover:bg-blue-600');
            button.classList.add('bg-green-500', 'hover:bg-green-600');
            this.activeConversion = null;
        }
    },

    handleError(error, button, buttonText, progressInfo, loadingSpinner) {
        ui.showToast(error.message || 'Conversion failed', 'error');
        
        if (button && buttonText) {
            buttonText.textContent = 'Error';
            button.disabled = false;
            loadingSpinner?.classList.add('hidden');
            button.classList.remove('bg-blue-500', 'hover:bg-blue-600');
            button.classList.add('bg-red-500', 'hover:bg-red-600');
            
            if (progressInfo) {
                progressInfo.textContent = `Error: ${error.message || 'Conversion failed'}`;
                progressInfo.classList.remove('hidden');
                progressInfo.classList.add('text-red-500');
            }
        }
        
        this.activeConversion = null;
    }
}; 