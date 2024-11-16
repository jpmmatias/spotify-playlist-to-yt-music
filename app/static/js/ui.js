// UI-related functionality
const ui = {
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 p-4 rounded-md shadow-lg ${
            type === 'error' ? 'bg-red-500' : 
            type === 'success' ? 'bg-green-500' : 
            type === 'warning' ? 'bg-yellow-500' : 
            'bg-blue-500'
        } text-white`;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.remove();
        }, 3000);
    },

    showYouTubeAuthModal() {
        const modal = document.getElementById('youtube-auth-modal');
        if (modal) {
            modal.classList.remove('hidden');
        } else {
            console.error('YouTube auth modal not found');
            this.showToast('Authentication modal not found', 'error');
        }
    },

    closeYouTubeAuthModal() {
        const modal = document.getElementById('youtube-auth-modal');
        if (modal) {
            modal.classList.add('hidden');
        }
    },

    updateButtonState(button, state, message = '') {
        const loadingSpinner = button.querySelector('.loading');
        const buttonText = button.querySelector('.text');
        const progressInfo = button.closest('.flex').querySelector('.progress-info');

        switch (state) {
            case 'loading':
                button.disabled = true;
                loadingSpinner.classList.remove('hidden');
                buttonText.textContent = message || 'Loading...';
                break;
            case 'error':
                button.disabled = false;
                loadingSpinner.classList.add('hidden');
                buttonText.textContent = message || 'Error';
                button.classList.remove('bg-blue-500', 'hover:bg-blue-600');
                button.classList.add('bg-red-500', 'hover:bg-red-600');
                break;
            case 'success':
                button.disabled = true;
                loadingSpinner.classList.add('hidden');
                buttonText.textContent = message || 'Success';
                button.classList.remove('bg-blue-500', 'hover:bg-blue-600');
                button.classList.add('bg-green-500', 'hover:bg-green-600');
                break;
            default:
                button.disabled = false;
                loadingSpinner.classList.add('hidden');
                buttonText.textContent = message || 'Convert';
                button.classList.remove('bg-red-500', 'hover:bg-red-600', 'bg-green-500', 'hover:bg-green-600');
                button.classList.add('bg-blue-500', 'hover:bg-blue-600');
        }

        if (progressInfo && message) {
            progressInfo.textContent = message;
            progressInfo.classList.remove('hidden');
        }
    }
}; 