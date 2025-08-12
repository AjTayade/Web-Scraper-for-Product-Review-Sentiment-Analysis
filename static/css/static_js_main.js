// Main JavaScript for Product Review Sentiment Analyzer

document.addEventListener('DOMContentLoaded', function() {
    // Initialize application
    initializeApp();
});

function initializeApp() {
    // Setup form validation
    setupFormValidation();

    // Setup loading modal
    setupLoadingModal();

    // Setup tooltips
    setupTooltips();

    // Setup smooth scrolling
    setupSmoothScrolling();

    // Setup copy functionality
    setupCopyToClipboard();
}

function setupFormValidation() {
    const form = document.getElementById('analyzeForm');
    const urlInput = document.getElementById('product_url');
    const submitBtn = document.getElementById('analyzeBtn');

    if (!form || !urlInput || !submitBtn) return;

    // Allowed domains for validation
    const allowedDomains = [
        'quotes.toscrape.com',
        'books.toscrape.com',
        'scrapethissite.com',
        'httpbin.org'
    ];

    // Real-time URL validation
    urlInput.addEventListener('input', function() {
        validateUrl(this.value);
    });

    // Form submission handling
    form.addEventListener('submit', function(e) {
        if (!validateUrl(urlInput.value)) {
            e.preventDefault();
            showError('Please enter a valid URL from one of our supported demo sites.');
            return;
        }

        // Show loading modal
        showLoadingModal();

        // Disable submit button to prevent double submission
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    });

    function validateUrl(url) {
        if (!url) return false;

        try {
            const urlObj = new URL(url);
            let domain = urlObj.hostname.toLowerCase();

            // Remove www. if present
            if (domain.startsWith('www.')) {
                domain = domain.substring(4);
            }

            const isValid = allowedDomains.includes(domain);

            // Update UI based on validation
            if (url && !isValid) {
                urlInput.classList.add('is-invalid');
                urlInput.classList.remove('is-valid');
            } else if (url && isValid) {
                urlInput.classList.add('is-valid');
                urlInput.classList.remove('is-invalid');
            } else {
                urlInput.classList.remove('is-valid', 'is-invalid');
            }

            return isValid;
        } catch (e) {
            urlInput.classList.add('is-invalid');
            urlInput.classList.remove('is-valid');
            return false;
        }
    }
}

function setupLoadingModal() {
    const loadingModal = document.getElementById('loadingModal');
    if (!loadingModal) return;

    // Create Bootstrap modal instance
    window.loadingModalInstance = new bootstrap.Modal(loadingModal, {
        backdrop: 'static',
        keyboard: false
    });
}

function showLoadingModal() {
    if (window.loadingModalInstance) {
        window.loadingModalInstance.show();
    }
}

function hideLoadingModal() {
    if (window.loadingModalInstance) {
        window.loadingModalInstance.hide();
    }
}

function setupTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function setupSmoothScrolling() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

function setupCopyToClipboard() {
    // Add copy buttons for code snippets
    document.querySelectorAll('code').forEach(codeBlock => {
        const wrapper = document.createElement('div');
        wrapper.style.position = 'relative';
        wrapper.style.display = 'inline-block';

        const copyBtn = document.createElement('button');
        copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
        copyBtn.className = 'btn btn-sm btn-outline-secondary ms-2';
        copyBtn.style.fontSize = '0.8rem';
        copyBtn.onclick = function() {
            copyToClipboard(codeBlock.textContent);
            copyBtn.innerHTML = '<i class="fas fa-check text-success"></i>';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        };

        codeBlock.parentNode.insertBefore(wrapper, codeBlock);
        wrapper.appendChild(codeBlock);
        wrapper.appendChild(copyBtn);
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showSuccess('Copied to clipboard!');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showSuccess('Copied to clipboard!');
    }
}

function showError(message) {
    showAlert(message, 'danger');
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showAlert(message, type) {
    const alertContainer = document.querySelector('.container.mt-3') || document.querySelector('.container');
    if (!alertContainer) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at the beginning of the container
    alertContainer.insertBefore(alertDiv, alertContainer.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Utility functions
function debounce(func, wait) {
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

function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatPercent(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(num / 100);
}

// Export functions for use in other scripts
window.AppUtils = {
    showError,
    showSuccess,
    showLoadingModal,
    hideLoadingModal,
    copyToClipboard,
    formatNumber,
    formatPercent
};
