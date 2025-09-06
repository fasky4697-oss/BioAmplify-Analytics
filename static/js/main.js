// Main JavaScript file for BioAmplify Analytics
// Handles global functionality, form validation, and utility functions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize global features
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeDataTables();
    
    // Navigation active state
    updateActiveNavigation();
    
    console.log('BioAmplify Analytics - JavaScript loaded successfully');
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Auto-dismiss alerts after 5 seconds
function initializeAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-permanent')) {
            setTimeout(() => {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }, 5000);
        }
    });
}

// Form validation utilities
function initializeFormValidation() {
    // Custom validation for confusion matrix
    const confusionInputs = document.querySelectorAll('input[name$="_positive"], input[name$="_negative"]');
    confusionInputs.forEach(input => {
        input.addEventListener('input', validateConfusionMatrix);
    });
    
    // File upload validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', validateFileUpload);
    });
}

// Validate confusion matrix inputs
function validateConfusionMatrix() {
    const tpInput = document.getElementById('true_positive');
    const fpInput = document.getElementById('false_positive');
    const tnInput = document.getElementById('true_negative');
    const fnInput = document.getElementById('false_negative');
    
    if (tpInput && fpInput && tnInput && fnInput) {
        const tp = parseInt(tpInput.value) || 0;
        const fp = parseInt(fpInput.value) || 0;
        const tn = parseInt(tnInput.value) || 0;
        const fn = parseInt(fnInput.value) || 0;
        
        const total = tp + fp + tn + fn;
        
        // Update total display
        const totalDisplay = document.getElementById('totalSamples');
        if (totalDisplay) {
            totalDisplay.textContent = total;
        }
        
        // Validation feedback
        const inputs = [tpInput, fpInput, tnInput, fnInput];
        inputs.forEach(input => {
            input.classList.remove('is-invalid', 'is-valid');
            const feedback = input.parentNode.querySelector('.invalid-feedback');
            if (feedback) feedback.remove();
        });
        
        // Check for valid data
        if (total === 0) {
            inputs.forEach(input => {
                input.classList.add('is-invalid');
                if (!input.parentNode.querySelector('.invalid-feedback')) {
                    const feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback';
                    feedback.textContent = 'At least one value must be greater than 0';
                    input.parentNode.appendChild(feedback);
                }
            });
        } else {
            inputs.forEach(input => {
                if (parseInt(input.value) >= 0) {
                    input.classList.add('is-valid');
                }
            });
            
            // Show warnings for unusual distributions
            showDataWarnings(tp, fp, tn, fn);
        }
    }
}

// Show warnings for unusual data patterns
function showDataWarnings(tp, fp, tn, fn) {
    const warningContainer = document.getElementById('dataWarnings');
    if (!warningContainer) return;
    
    const total = tp + fp + tn + fn;
    const positive = tp + fn;
    const negative = fp + tn;
    
    let warnings = [];
    
    // Small sample size
    if (total < 10) {
        warnings.push('Small sample size may lead to unreliable statistical estimates');
    }
    
    // Highly imbalanced dataset
    if (positive > 0 && negative > 0) {
        const ratio = Math.max(positive, negative) / Math.min(positive, negative);
        if (ratio > 10) {
            warnings.push(`Highly imbalanced dataset (ratio: ${ratio.toFixed(1)}:1)`);
        }
    }
    
    // Perfect classification
    if (fp === 0 && fn === 0 && total > 0) {
        warnings.push('Perfect classification detected - verify data accuracy');
    }
    
    // No correct classifications
    if (tp === 0 && tn === 0 && total > 0) {
        warnings.push('No correct classifications detected - verify data accuracy');
    }
    
    // Update warning display
    if (warnings.length > 0) {
        warningContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Data Quality Warnings:</strong>
                <ul class="mb-0 mt-2">
                    ${warnings.map(w => `<li>${w}</li>`).join('')}
                </ul>
            </div>
        `;
        warningContainer.style.display = 'block';
    } else {
        warningContainer.style.display = 'none';
    }
}

// Validate file uploads
function validateFileUpload(event) {
    const file = event.target.files[0];
    const feedback = event.target.parentNode.querySelector('.invalid-feedback') ||
                    document.createElement('div');
    
    feedback.className = 'invalid-feedback';
    
    if (file) {
        const fileName = file.name.toLowerCase();
        const validExtensions = ['.csv', '.xlsx', '.xls'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        let isValid = true;
        let errorMessage = '';
        
        // Check file extension
        if (!validExtensions.some(ext => fileName.endsWith(ext))) {
            isValid = false;
            errorMessage = 'Please select a valid CSV or Excel file';
        }
        
        // Check file size
        if (file.size > maxSize) {
            isValid = false;
            errorMessage = 'File size must be less than 10MB';
        }
        
        // Update UI
        event.target.classList.remove('is-invalid', 'is-valid');
        
        if (isValid) {
            event.target.classList.add('is-valid');
            if (feedback.parentNode) feedback.remove();
        } else {
            event.target.classList.add('is-invalid');
            feedback.textContent = errorMessage;
            if (!feedback.parentNode) {
                event.target.parentNode.appendChild(feedback);
            }
        }
    }
}

// Initialize DataTables with common configuration
function initializeDataTables() {
    const tables = document.querySelectorAll('.data-table');
    tables.forEach(table => {
        if (table && !$.fn.DataTable.isDataTable(table)) {
            $(table).DataTable({
                responsive: true,
                pageLength: 25,
                order: [[0, 'desc']],
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>t<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>',
                language: {
                    search: "Search experiments:",
                    lengthMenu: "Show _MENU_ experiments per page",
                    info: "Showing _START_ to _END_ of _TOTAL_ experiments",
                    emptyTable: "No experiments found"
                }
            });
        }
    });
}

// Update active navigation item
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href && currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        } else if (href === '/' && currentPath === '/') {
            link.classList.add('active');
        }
    });
}

// Utility function to format numbers
function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return 'N/A';
    if (num === Infinity) return '∞';
    if (num === -Infinity) return '-∞';
    return parseFloat(num).toFixed(decimals);
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('th-TH', {
        style: 'currency',
        currency: 'THB'
    }).format(amount);
}

// Utility function to format percentages
function formatPercentage(value, decimals = 1) {
    if (value === null || value === undefined) return 'N/A';
    return `${parseFloat(value).toFixed(decimals)}%`;
}

// Show loading spinner
function showLoading(element) {
    const spinner = document.createElement('div');
    spinner.className = 'text-center p-3';
    spinner.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
        <div class="mt-2">Processing...</div>
    `;
    
    element.innerHTML = '';
    element.appendChild(spinner);
}

// Hide loading spinner
function hideLoading(element, content) {
    element.innerHTML = content;
}

// Copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

// Show toast notification
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

// Chart color schemes
const chartColors = {
    primary: '#0d6efd',
    secondary: '#6c757d',
    success: '#198754',
    info: '#0dcaf0',
    warning: '#ffc107',
    danger: '#dc3545',
    light: '#f8f9fa',
    dark: '#212529'
};

// Get technique color
function getTechniqueColor(technique) {
    const colors = {
        'qPCR': chartColors.primary,
        'LAMP': chartColors.success,
        'RPA': chartColors.danger,
        'NASBA': chartColors.warning
    };
    return colors[technique] || chartColors.secondary;
}

// Create responsive chart options
function getResponsiveChartOptions(title = '', yAxisLabel = '') {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            title: {
                display: !!title,
                text: title,
                font: {
                    size: 16,
                    weight: 'bold'
                }
            },
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: yAxisLabel ? {
            y: {
                title: {
                    display: true,
                    text: yAxisLabel
                }
            }
        } : {}
    };
}

// Export functions for use in other scripts
window.BioAmplify = {
    formatNumber,
    formatCurrency,
    formatPercentage,
    showLoading,
    hideLoading,
    copyToClipboard,
    showToast,
    chartColors,
    getTechniqueColor,
    getResponsiveChartOptions,
    validateConfusionMatrix,
    validateFileUpload
};

// Handle back button for results pages
if (window.location.pathname.includes('/experiment/') || window.location.pathname.includes('/compare')) {
    window.addEventListener('beforeunload', function() {
        sessionStorage.setItem('returnToAnalysis', 'true');
    });
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter or Cmd+Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const activeForm = document.querySelector('form:focus-within');
        if (activeForm) {
            const submitBtn = activeForm.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.click();
            }
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const openModal = document.querySelector('.modal.show');
        if (openModal) {
            const bsModal = bootstrap.Modal.getInstance(openModal);
            if (bsModal) bsModal.hide();
        }
    }
});

// Print functionality
function printResults() {
    window.print();
}

// Export table data as CSV
function exportTableAsCSV(tableId, filename = 'data.csv') {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const rows = Array.from(table.querySelectorAll('tr'));
    const csv = rows.map(row => {
        const cells = Array.from(row.querySelectorAll('th, td'));
        return cells.map(cell => {
            const text = cell.textContent.replace(/"/g, '""');
            return `"${text}"`;
        }).join(',');
    }).join('\n');
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}
