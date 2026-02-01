// WeChat Auto-Reply Bot - Frontend JavaScript

// DOM elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const refreshBtn = document.getElementById('refreshBtn');
const statusBadge = document.getElementById('statusBadge');
const statusText = statusBadge.querySelector('.status-text');
const configForm = document.getElementById('configForm');
const logsContainer = document.getElementById('logs');
const trackingContainer = document.getElementById('tracking');

// State
let isRunning = false;
let logsPollInterval = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    updateStatus();
    loadTracking();
    startLogPolling();
});

// Load configuration
async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();

        // Populate form
        document.getElementById('chat_name').value = config.chat_name || '';
        document.getElementById('user_name').value = config.user_name || '';
        document.getElementById('user_title').value = config.user_title || '';
        document.getElementById('intro_template').value = config.intro_template || '';
        document.getElementById('default_reply').value = config.default_reply || '';
        document.getElementById('reply_mode').value = config.reply_mode || 'c';
        document.getElementById('dry_run').value = config.dry_run || 'yes';
    } catch (error) {
        console.error('Failed to load config:', error);
        addLogEntry('Failed to load configuration', 'error');
    }
}

// Save configuration
configForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const config = {
        chat_name: document.getElementById('chat_name').value,
        user_name: document.getElementById('user_name').value,
        user_title: document.getElementById('user_title').value,
        intro_template: document.getElementById('intro_template').value,
        default_reply: document.getElementById('default_reply').value,
        reply_mode: document.getElementById('reply_mode').value,
        dry_run: document.getElementById('dry_run').value
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        if (response.ok) {
            addLogEntry('Configuration saved successfully', 'success');
        } else {
            throw new Error('Failed to save configuration');
        }
    } catch (error) {
        console.error('Failed to save config:', error);
        addLogEntry('Failed to save configuration', 'error');
    }
});

// Update status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();

        isRunning = status.running;
        updateUI();
    } catch (error) {
        console.error('Failed to update status:', error);
    }
}

// Update UI based on status
function updateUI() {
    if (isRunning) {
        statusBadge.classList.add('running');
        statusText.textContent = 'Running';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusBadge.classList.remove('running');
        statusText.textContent = 'Stopped';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

// Start bot
startBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/start', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            addLogEntry('Bot started', 'success');
            setTimeout(updateStatus, 500);
        } else {
            addLogEntry(`Failed to start: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Failed to start bot:', error);
        addLogEntry('Failed to start bot', 'error');
    }
});

// Stop bot
stopBtn.addEventListener('click', async () => {
    try {
        const response = await fetch('/api/stop', { method: 'POST' });
        const result = await response.json();

        if (result.success) {
            addLogEntry('Bot stopped', 'info');
            setTimeout(updateStatus, 500);
        } else {
            addLogEntry(`Failed to stop: ${result.error}`, 'error');
        }
    } catch (error) {
        console.error('Failed to stop bot:', error);
        addLogEntry('Failed to stop bot', 'error');
    }
});

// Refresh status
refreshBtn.addEventListener('click', () => {
    updateStatus();
    loadLogs();
    loadTracking();
    addLogEntry('Status refreshed', 'info');
});

// Load logs
async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const logs = await response.json();

        logsContainer.innerHTML = '';

        if (logs.length === 0) {
            logsContainer.innerHTML = '<p class="text-muted">No logs yet</p>';
            return;
        }

        logs.forEach(log => {
            addLogEntry(log.message, log.level, log.timestamp, false);
        });

        // Scroll to bottom
        logsContainer.scrollTop = logsContainer.scrollHeight;
    } catch (error) {
        console.error('Failed to load logs:', error);
    }
}

// Add log entry
function addLogEntry(message, level = 'info', timestamp = null, scroll = true) {
    if (!timestamp) {
        const now = new Date();
        timestamp = now.toLocaleTimeString('en-US', { hour12: false });
    }

    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${level}`;
    logEntry.innerHTML = `
        <span class="timestamp">${timestamp}</span>
        <span class="message">${escapeHtml(message)}</span>
    `;

    logsContainer.appendChild(logEntry);

    if (scroll) {
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }
}

// Load tracking data
async function loadTracking() {
    try {
        const response = await fetch('/api/tracking');
        const tracking = await response.json();

        trackingContainer.innerHTML = '';

        if (tracking.length === 0) {
            trackingContainer.innerHTML = '<p class="text-muted">No contacts tracked yet</p>';
            return;
        }

        tracking.forEach(contact => {
            const item = document.createElement('div');
            item.className = 'tracking-item';
            item.textContent = contact;
            trackingContainer.appendChild(item);
        });
    } catch (error) {
        console.error('Failed to load tracking:', error);
    }
}

// Start polling logs
function startLogPolling() {
    logsPollInterval = setInterval(() => {
        if (isRunning) {
            loadLogs();
        }
        updateStatus();
    }, 2000); // Poll every 2 seconds
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initial load
loadLogs();