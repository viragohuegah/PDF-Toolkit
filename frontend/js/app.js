/* ============================================
   PDF TOOLKIT - MAIN APPLICATION
   ============================================ */

// PAGE NAVIGATION
function navigateTo(page, ev = window.event) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.querySelectorAll('.feature-page').forEach(p => p.remove());

    // Remove active state from nav links
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));

    // Add active state to clicked link
    ev?.target?.closest('.nav-link')?.classList.add('active');

    // Update page title
    const titles = {
        'dashboard': 'Dashboard',
        'compress': 'Compress PDF',
        'merge': 'Merge PDFs',
        'split': 'Split PDF',
        'pdf-to-image': 'PDF to Image',
        'image-to-pdf': 'Image to PDF',
        'pdf-to-text': 'PDF to Text',
        'pdf-to-word': 'PDF to Word',
        'protect': 'Protect PDF',
        'unlock': 'Unlock PDF',
        'restrict': 'Restrict PDF',
        'watermark': 'Add Watermark',
        'history': 'Download History'
    };

    document.getElementById('pageTitle').textContent = titles[page] || page;

    if (page === 'dashboard') {
        document.getElementById('dashboard').classList.add('active');
    } else {
        loadPage(page);
    }
}

// LOAD PAGE CONTENT
async function loadPage(page) {
    const pageMap = {
        'compress': '/frontend/pages/compress.html',
        'merge': '/frontend/pages/merge.html',
        'split': '/frontend/pages/split.html',
        'pdf-to-image': '/frontend/pages/pdf-to-image.html',
        'image-to-pdf': '/frontend/pages/image-to-pdf.html',
        'pdf-to-text': '/frontend/pages/pdf-to-text.html',
        'pdf-to-word': '/frontend/pages/pdf-to-word.html',
        'protect': '/frontend/pages/protect.html',
        'unlock': '/frontend/pages/unlock.html',
        'restrict': '/frontend/pages/restrict.html',
        'watermark': '/frontend/pages/watermark.html',
        'history': '/frontend/pages/history.html'
    };

    try {
        const response = await fetch(pageMap[page]);
        const html = await response.text();
        const contentArea = document.getElementById('content-area');
        contentArea.innerHTML = html;

        // Execute any scripts in the loaded content
        contentArea.querySelectorAll('script').forEach(script => {
            const newScript = document.createElement('script');
            newScript.textContent = script.textContent;
            document.body.appendChild(newScript);
        });
    } catch (error) {
        console.error('Error loading page:', error);
        showToast('Error loading page', 'error');
    }
}

// TOAST NOTIFICATIONS
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };

    toast.innerHTML = `
        <i class="${icons[type] || icons['info']}"></i>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 4000);
}

// MODAL MANAGEMENT
function openModal(content) {
    document.getElementById('modalBody').innerHTML = content;
    document.getElementById('modal').classList.remove('hidden');
}

function closeModal() {
    document.getElementById('modal').classList.add('hidden');
}

// THEME TOGGLE
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const isDarkMode = localStorage.getItem('darkMode') === 'true';

    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }

    themeToggle.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDark = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDark);
        themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
    });
}

// SIDEBAR TOGGLE
function initSidebar() {
    const toggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');

    if (toggle) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
        });
    }

    // Close sidebar on mobile when clicking a nav link
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                sidebar.classList.add('collapsed');
            }
        });
    });
}

// INITIALIZE APP
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSidebar();

    // Set dashboard as default active page
    document.querySelector('.nav-link').classList.add('active');

    // Close modal when clicking outside
    document.getElementById('modal').addEventListener('click', (e) => {
        if (e.target.id === 'modal') {
            closeModal();
        }
    });
});

// API HELPER FUNCTIONS
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Accept': 'application/json'
        }
    };

    if (data && method !== 'GET') {
        options.body = data;
    }

    try {
        const response = await fetch(endpoint, options);
        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Get file extension
function getFileExtension(filename) {
    return filename.split('.').pop().toLowerCase();
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// Generate UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Export functions for use in feature pages
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
window.navigateTo = navigateTo;
window.formatFileSize = formatFileSize;
