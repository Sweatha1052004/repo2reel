// Repo2Reel Frontend JavaScript
// Handles form validation, user interactions, and UI enhancements

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initializeFormValidation();
    initializeUIEnhancements();
    initializeTooltips();
    
    console.log('Repo2Reel frontend initialized');
});

/**
 * Initialize form validation for GitHub URL input
 */
function initializeFormValidation() {
    const form = document.getElementById('repoForm');
    const urlInput = document.getElementById('github_url');
    const submitBtn = document.getElementById('generateBtn');
    
    if (!form || !urlInput || !submitBtn) {
        return; // Elements not found, probably not on main page
    }
    
    // Real-time URL validation
    urlInput.addEventListener('input', function() {
        validateGitHubURL(this.value);
    });
    
    // Form submission handling
    form.addEventListener('submit', function(e) {
        const url = urlInput.value.trim();
        
        if (!validateGitHubURL(url)) {
            e.preventDefault();
            showValidationError('Please enter a valid GitHub repository URL');
            return false;
        }
        
        // Show loading state
        showLoadingState();
        
        // Allow form to submit normally
        return true;
    });
    
    // Handle paste events for URL cleanup
    urlInput.addEventListener('paste', function(e) {
        setTimeout(() => {
            const pastedText = this.value.trim();
            if (pastedText) {
                // Clean up common URL variations
                const cleanedURL = cleanGitHubURL(pastedText);
                if (cleanedURL !== pastedText) {
                    this.value = cleanedURL;
                    validateGitHubURL(cleanedURL);
                }
            }
        }, 10);
    });
}

/**
 * Validate GitHub URL format
 * @param {string} url - The URL to validate
 * @returns {boolean} - Whether the URL is valid
 */
function validateGitHubURL(url) {
    if (!url) {
        clearValidationState();
        return false;
    }
    
    // GitHub URL patterns
    const githubPatterns = [
        /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/,
        /^http:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\/?$/,
        /^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\.git$/
    ];
    
    const isValid = githubPatterns.some(pattern => pattern.test(url));
    
    if (isValid) {
        showValidationSuccess();
    } else {
        showValidationError('Please enter a valid GitHub repository URL (e.g., https://github.com/user/repo)');
    }
    
    return isValid;
}

/**
 * Clean and normalize GitHub URLs
 * @param {string} url - The URL to clean
 * @returns {string} - The cleaned URL
 */
function cleanGitHubURL(url) {
    if (!url) return url;
    
    // Remove trailing slashes and .git extensions
    url = url.trim().replace(/\/+$/, '').replace(/\.git$/, '');
    
    // Convert GitHub clone URLs to web URLs
    if (url.startsWith('git@github.com:')) {
        url = url.replace('git@github.com:', 'https://github.com/');
    }
    
    // Ensure https protocol
    if (url.startsWith('http://github.com/')) {
        url = url.replace('http://', 'https://');
    }
    
    // Handle github.com without protocol
    if (url.startsWith('github.com/') && !url.startsWith('https://')) {
        url = 'https://' + url;
    }
    
    return url;
}

/**
 * Show validation success state
 */
function showValidationSuccess() {
    const urlInput = document.getElementById('github_url');
    const submitBtn = document.getElementById('generateBtn');
    
    if (urlInput) {
        urlInput.classList.remove('is-invalid');
        urlInput.classList.add('is-valid');
    }
    
    if (submitBtn) {
        submitBtn.disabled = false;
    }
    
    clearValidationMessage();
}

/**
 * Show validation error state
 * @param {string} message - Error message to display
 */
function showValidationError(message) {
    const urlInput = document.getElementById('github_url');
    const submitBtn = document.getElementById('generateBtn');
    
    if (urlInput) {
        urlInput.classList.remove('is-valid');
        urlInput.classList.add('is-invalid');
    }
    
    if (submitBtn) {
        submitBtn.disabled = true;
    }
    
    showValidationMessage(message, 'error');
}

/**
 * Clear validation state
 */
function clearValidationState() {
    const urlInput = document.getElementById('github_url');
    const submitBtn = document.getElementById('generateBtn');
    
    if (urlInput) {
        urlInput.classList.remove('is-valid', 'is-invalid');
    }
    
    if (submitBtn) {
        submitBtn.disabled = false;
    }
    
    clearValidationMessage();
}

/**
 * Show validation message
 * @param {string} message - Message to display
 * @param {string} type - Message type ('error', 'success', 'info')
 */
function showValidationMessage(message, type = 'info') {
    // Remove existing validation messages
    clearValidationMessage();
    
    const urlInput = document.getElementById('github_url');
    if (!urlInput) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `validation-message alert alert-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} mt-2`;
    messageDiv.innerHTML = `<small>${message}</small>`;
    messageDiv.id = 'url-validation-message';
    
    // Insert after the input group
    const inputGroup = urlInput.closest('.input-group');
    if (inputGroup && inputGroup.parentNode) {
        inputGroup.parentNode.insertBefore(messageDiv, inputGroup.nextSibling);
    }
}

/**
 * Clear validation message
 */
function clearValidationMessage() {
    const existingMessage = document.getElementById('url-validation-message');
    if (existingMessage) {
        existingMessage.remove();
    }
}

/**
 * Show loading state when form is submitted
 */
function showLoadingState() {
    const submitBtn = document.getElementById('generateBtn');
    if (!submitBtn) return;
    
    const originalContent = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    submitBtn.disabled = true;
    
    // Store original content for potential restoration
    submitBtn.setAttribute('data-original-content', originalContent);
}

/**
 * Initialize UI enhancements
 */
function initializeUIEnhancements() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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
    
    // Auto-dismiss alerts after 10 seconds
    document.querySelectorAll('.alert:not(.alert-permanent)').forEach(alert => {
        setTimeout(() => {
            if (alert && alert.parentNode) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 10000);
    });
    
    // Add ripple effect to buttons
    addRippleEffect();
    
    // Initialize progressive enhancement features
    initializeProgressiveEnhancements();
}

/**
 * Add ripple effect to buttons
 */
function addRippleEffect() {
    document.querySelectorAll('.btn').forEach(button => {
        button.addEventListener('click', function(e) {
            // Skip if button is disabled
            if (this.disabled) return;
            
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Add custom tooltips for form elements
    const urlInput = document.getElementById('github_url');
    if (urlInput && !urlInput.hasAttribute('title')) {
        urlInput.setAttribute('title', 'Enter the full GitHub repository URL (e.g., https://github.com/username/repository)');
        new bootstrap.Tooltip(urlInput);
    }
}

/**
 * Initialize progressive enhancement features
 */
function initializeProgressiveEnhancements() {
    // Check for advanced browser features
    const hasIntersectionObserver = 'IntersectionObserver' in window;
    const hasClipboardAPI = navigator.clipboard && navigator.clipboard.writeText;
    
    // Add animation on scroll if supported
    if (hasIntersectionObserver) {
        initializeScrollAnimations();
    }
    
    // Enhanced clipboard functionality
    if (hasClipboardAPI) {
        enhanceClipboardFeatures();
    }
    
    // Check for service worker support
    if ('serviceWorker' in navigator) {
        // Could add offline functionality in the future
        console.log('Service Worker support detected');
    }
}

/**
 * Initialize scroll-triggered animations
 */
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements that should animate in
    document.querySelectorAll('.card, .row > .col-md-4').forEach(el => {
        el.classList.add('animate-on-scroll');
        observer.observe(el);
    });
}

/**
 * Enhance clipboard features
 */
function enhanceClipboardFeatures() {
    // Add clipboard functionality to code examples (if any)
    document.querySelectorAll('pre, code').forEach(codeBlock => {
        if (codeBlock.textContent.length > 20) {
            const copyButton = document.createElement('button');
            copyButton.className = 'btn btn-sm btn-outline-secondary copy-code-btn';
            copyButton.innerHTML = '<i class="fas fa-copy"></i>';
            copyButton.title = 'Copy to clipboard';
            
            copyButton.addEventListener('click', () => {
                navigator.clipboard.writeText(codeBlock.textContent).then(() => {
                    copyButton.innerHTML = '<i class="fas fa-check"></i>';
                    copyButton.classList.add('btn-success');
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                        copyButton.classList.remove('btn-success');
                    }, 2000);
                });
            });
            
            // Position the button
            codeBlock.style.position = 'relative';
            copyButton.style.position = 'absolute';
            copyButton.style.top = '5px';
            copyButton.style.right = '5px';
            codeBlock.appendChild(copyButton);
        }
    });
}

/**
 * Handle processing page functionality
 */
function initializeProcessingPage() {
    // This function is called from the processing page template
    const progressBar = document.getElementById('progressBar');
    const statusMessage = document.getElementById('statusMessage');
    const stepItems = document.querySelectorAll('.step-item');
    
    if (!progressBar || !statusMessage) {
        return; // Not on processing page
    }
    
    // Add processing animations
    document.body.classList.add('processing-mode');
    
    // Animate step indicators based on progress
    function updateStepAnimations(progress) {
        stepItems.forEach(item => {
            const stepProgress = parseInt(item.getAttribute('data-step'));
            const icon = item.querySelector('.step-icon');
            const check = item.querySelector('.step-check');
            
            if (progress >= stepProgress) {
                item.classList.add('step-completed');
                if (icon) icon.classList.add('text-success');
                if (check) check.classList.remove('d-none');
            } else if (progress >= stepProgress - 20) {
                item.classList.add('step-active');
                if (icon) icon.classList.add('text-primary');
            }
        });
    }
    
    // Initial animation
    const currentProgress = parseInt(progressBar.getAttribute('aria-valuenow')) || 0;
    updateStepAnimations(currentProgress);
    
    // Add pulse animation to active elements
    const activeElements = document.querySelectorAll('.spinner-border, .progress-bar-animated');
    activeElements.forEach(el => {
        el.classList.add('pulse-animation');
    });
}

/**
 * Handle result page functionality
 */
function initializeResultPage() {
    // Add success animations
    const successIcon = document.querySelector('.fa-check-circle');
    if (successIcon) {
        setTimeout(() => {
            successIcon.classList.add('success-animation');
        }, 500);
    }
    
    // Auto-focus on download button
    const downloadBtn = document.querySelector('a[download]');
    if (downloadBtn) {
        setTimeout(() => {
            downloadBtn.focus();
        }, 1000);
    }
}

/**
 * Utility function to show temporary notifications
 * @param {string} message - Message to show
 * @param {string} type - Notification type ('success', 'error', 'info')
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show notification-toast`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Style the notification
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    notification.style.maxWidth = '500px';
    
    document.body.appendChild(notification);
    
    // Auto-dismiss
    setTimeout(() => {
        if (notification.parentNode) {
            const bsAlert = new bootstrap.Alert(notification);
            bsAlert.close();
        }
    }, duration);
}

/**
 * Debounce function for performance optimization
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
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

/**
 * Throttle function for performance optimization
 * @param {Function} func - Function to throttle
 * @param {number} limit - Limit in milliseconds
 * @returns {Function} - Throttled function
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Global functions for template usage
window.showNotification = showNotification;
window.initializeProcessingPage = initializeProcessingPage;
window.initializeResultPage = initializeResultPage;

// Add some CSS for animations and effects
const style = document.createElement('style');
style.textContent = `
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .animate-on-scroll {
        opacity: 0;
        transform: translateY(30px);
        transition: all 0.6s ease;
    }
    
    .animate-in {
        opacity: 1;
        transform: translateY(0);
    }
    
    .success-animation {
        animation: successBounce 0.8s ease-in-out;
    }
    
    @keyframes successBounce {
        0% { transform: scale(0); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .processing-mode .card {
        animation: processingGlow 3s ease-in-out infinite alternate;
    }
    
    @keyframes processingGlow {
        from { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
        to { box-shadow: 0 0 30px rgba(102, 126, 234, 0.6); }
    }
    
    .step-completed {
        background: rgba(40, 167, 69, 0.1) !important;
        border-left: 4px solid #28a745 !important;
    }
    
    .step-active {
        background: rgba(102, 126, 234, 0.1) !important;
        border-left: 4px solid #667eea !important;
    }
    
    .copy-code-btn {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    pre:hover .copy-code-btn,
    code:hover .copy-code-btn {
        opacity: 1;
    }
    
    .notification-toast {
        animation: slideInRight 0.3s ease;
    }
    
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .validation-message {
        font-size: 0.875rem;
        margin-top: 0.25rem;
        padding: 0.5rem 0.75rem;
        border-radius: 0.375rem;
    }
`;

document.head.appendChild(style);

console.log('Repo2Reel JavaScript loaded successfully');
