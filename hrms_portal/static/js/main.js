/**
 * HRMS Portal - Main JavaScript
 * Common functionality and utilities
 */

// ==================== MESSAGE SYSTEM ====================

/**
 * Show a message notification
 * @param {string} message - The message to display
 * @param {string} type - Message type (success, error, warning, info)
 * @param {number} duration - Duration in milliseconds
 */
function showMessage(message, type = 'info', duration = 5000) {
    const container = document.getElementById('messages-container');
    if (!container) return;
    
    // Create message element
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.innerHTML = `
        <span class="message-text">${escapeHtml(message)}</span>
        <button class="message-close" onclick="closeMessage(this)">&times;</button>
    `;
    
    // Add to container
    container.appendChild(messageEl);
    
    // Auto-remove after duration
    if (duration > 0) {
        setTimeout(() => {
            removeMessage(messageEl);
        }, duration);
    }
}

/**
 * Close a message notification
 * @param {HTMLElement} button - The close button element
 */
function closeMessage(button) {
    const messageEl = button.closest('.message');
    if (messageEl) {
        removeMessage(messageEl);
    }
}

/**
 * Remove a message element with animation
 * @param {HTMLElement} messageEl - The message element to remove
 */
function removeMessage(messageEl) {
    messageEl.style.animation = 'slideOut 0.3s ease forwards';
    setTimeout(() => {
        if (messageEl.parentNode) {
            messageEl.parentNode.removeChild(messageEl);
        }
    }, 300);
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== UTILITY FUNCTIONS ====================

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format a date string
 * @param {string} dateString - ISO date string
 * @param {object} options - Intl.DateTimeFormat options
 * @returns {string} Formatted date
 */
function formatDate(dateString, options = {}) {
    const date = new Date(dateString);
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    };
    return new Intl.DateTimeFormat('en-US', { ...defaultOptions, ...options }).format(date);
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit time in milliseconds
 * @returns {Function} Throttled function
 */
function throttle(func, limit = 300) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ==================== FORM VALIDATION ====================

/**
 * Validate an email address
 * @param {string} email - Email to validate
 * @returns {boolean} Is valid
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate a date range
 * @param {string} startDate - Start date string
 * @param {string} endDate - End date string
 * @returns {boolean} Is valid
 */
function isValidDateRange(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return start <= end;
}

/**
 * Calculate days between two dates
 * @param {string} startDate - Start date string
 * @param {string} endDate - End date string
 * @returns {number} Number of days
 */
function calculateDays(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end - start);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
}

// ==================== AJAX HELPERS ====================

/**
 * Make an AJAX request
 * @param {string} url - URL to fetch
 * @param {object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
async function ajax(url, options = {}) {
    const defaultOptions = {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    };
    
    // Add CSRF token for non-GET requests
    if (options.method && options.method !== 'GET') {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        if (csrfToken) {
            defaultOptions.headers['X-CSRFToken'] = csrfToken;
        }
    }
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(url, mergedOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('AJAX Error:', error);
        throw error;
    }
}

// ==================== REAL-TIME UPDATES ====================

/**
 * Poll for updates
 * @param {string} url - URL to poll
 * @param {Function} callback - Callback function
 * @param {number} interval - Polling interval in milliseconds
 * @returns {number} Interval ID
 */
function startPolling(url, callback, interval = 10000) {
    const poll = async () => {
        try {
            const data = await ajax(url);
            callback(data);
        } catch (error) {
            console.error('Polling error:', error);
        }
    };
    
    // Initial poll
    poll();
    
    // Start interval
    return setInterval(poll, interval);
}

/**
 * Stop polling
 * @param {number} intervalId - Interval ID from startPolling
 */
function stopPolling(intervalId) {
    clearInterval(intervalId);
}

// ==================== UI HELPERS ====================

/**
 * Toggle element visibility
 * @param {string|HTMLElement} element - Element or selector
 * @param {boolean} show - Show or hide
 */
function toggleElement(element, show) {
    const el = typeof element === 'string' ? document.querySelector(element) : element;
    if (el) {
        el.style.display = show ? '' : 'none';
    }
}

/**
 * Add loading state to button
 * @param {HTMLElement} button - Button element
 * @param {string} loadingText - Text to show while loading
 */
function setButtonLoading(button, loadingText = 'Loading...') {
    button.dataset.originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner"></span> ${loadingText}`;
    button.disabled = true;
}

/**
 * Remove loading state from button
 * @param {HTMLElement} button - Button element
 */
function removeButtonLoading(button) {
    if (button.dataset.originalText) {
        button.innerHTML = button.dataset.originalText;
    }
    button.disabled = false;
}

// Add spinner styles
const spinnerStyle = document.createElement('style');
spinnerStyle.textContent = `
    .spinner {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-top-color: white;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(spinnerStyle);

// ==================== INITIALIZATION ====================

/**
 * Initialize common functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.message');
    messages.forEach(message => {
        setTimeout(() => {
            removeMessage(message);
        }, 5000);
    });
    
    // Add click outside handler for dropdowns
    document.addEventListener('click', function(e) {
        const dropdowns = document.querySelectorAll('.dropdown.active');
        dropdowns.forEach(dropdown => {
            if (!dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    });
    
    // Handle form submissions with loading state
    const forms = document.querySelectorAll('form[data-loading]');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                setButtonLoading(submitBtn, form.dataset.loading);
            }
        });
    });
});

// ==================== EXPORT ====================

// Make functions available globally
window.showMessage = showMessage;
window.closeMessage = closeMessage;
window.escapeHtml = escapeHtml;
window.formatDate = formatDate;
window.debounce = debounce;
window.throttle = throttle;
window.isValidEmail = isValidEmail;
window.isValidDateRange = isValidDateRange;
window.calculateDays = calculateDays;
window.ajax = ajax;
window.startPolling = startPolling;
window.stopPolling = stopPolling;
window.toggleElement = toggleElement;
window.setButtonLoading = setButtonLoading;
window.removeButtonLoading = removeButtonLoading;
