/* ============================================
   DOWNLOAD HISTORY MANAGEMENT
   ============================================ */

// Save to download history (sessionStorage)
function saveToHistory(operation, originalFile, outputFile) {
    let history = getDownloadHistory();

    const entry = {
        id: generateUUID(),
        operation: operation,
        originalFile: originalFile,
        outputFile: outputFile,
        timestamp: new Date().toISOString()
    };

    history.unshift(entry); // Add to beginning

    // Keep only last 50 items
    if (history.length > 50) {
        history = history.slice(0, 50);
    }

    sessionStorage.setItem('downloadHistory', JSON.stringify(history));
    showToast(`${operation} added to history`, 'success');
}

// Get download history
function getDownloadHistory() {
    const history = sessionStorage.getItem('downloadHistory');
    return history ? JSON.parse(history) : [];
}

// Clear download history
function clearDownloadHistory() {
    if (confirm('Are you sure you want to clear all download history?')) {
        sessionStorage.removeItem('downloadHistory');
        showToast('History cleared', 'success');
        // Refresh history display if visible
        if (document.getElementById('historyTableBody')) {
            displayDownloadHistory();
        }
    }
}

// Display history in table
function displayDownloadHistory() {
    const history = getDownloadHistory();
    const tableBody = document.getElementById('historyTableBody');
    const emptyHistory = document.getElementById('emptyHistory');
    const historyTable = document.getElementById('historyTable');

    if (!tableBody) return;

    if (history.length === 0) {
        historyTable.style.display = 'none';
        if (emptyHistory) emptyHistory.style.display = 'block';
        return;
    }

    historyTable.style.display = 'block';
    if (emptyHistory) emptyHistory.style.display = 'none';

    tableBody.innerHTML = '';

    history.forEach((item) => {
        const row = document.createElement('tr');
        const date = new Date(item.timestamp);
        const formattedDate = date.toLocaleString();

        row.innerHTML = `
            <td>
                <span class="badge">${item.operation}</span>
            </td>
            <td>
                <small>${item.originalFile}</small>
            </td>
            <td>
                <small>${item.outputFile}</small>
            </td>
            <td>
                <small>${formattedDate}</small>
            </td>
            <td>
                <button class="btn btn-small" title="Download">
                    <i class="fas fa-download"></i>
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });

    // Update stats
    updateStats(history);
}

// Update dashboard stats
function updateStats(history) {
    const statsElements = document.querySelectorAll('.stat-number');
    
    if (statsElements.length >= 3) {
        // Total files processed
        statsElements[0].textContent = history.length;

        // Total size (estimate: 5MB average)
        const totalSize = (history.length * 5).toFixed(1);
        statsElements[1].textContent = totalSize + ' MB';

        // Today's count
        const today = new Date().toDateString();
        const todayCount = history.filter(item => 
            new Date(item.timestamp).toDateString() === today
        ).length;
        statsElements[2].textContent = todayCount;
    }
}

// Initialize history on load
document.addEventListener('DOMContentLoaded', () => {
    const history = getDownloadHistory();
    updateStats(history);
});

// Export for global use
window.saveToHistory = saveToHistory;
window.getDownloadHistory = getDownloadHistory;
window.clearDownloadHistory = clearDownloadHistory;
window.displayDownloadHistory = displayDownloadHistory;
