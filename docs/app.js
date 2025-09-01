// Static demo version of EduHealth JavaScript

// Tab switching functionality
function switchTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.dashboard-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    event.target.classList.add('active');
    document.getElementById(tabName + '-tab').classList.add('active');
}

// Modal functionality
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

function switchToRegister() {
    closeModal('loginModal');
    openModal('registerModal');
}

function switchToLogin() {
    closeModal('registerModal');
    openModal('loginModal');
}

// Demo message for payment
function showDemoMessage() {
    alert('This is a demo version. Payment functionality is available in the full application. Visit the GitHub repository for the complete source code.');
}

// Form submissions (demo only)
document.addEventListener('DOMContentLoaded', function() {
    // Login form
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Demo login successful! In the full version, you would be logged into your dashboard.');
        closeModal('loginModal');
    });
    
    // Register form
    document.getElementById('registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Demo registration successful! In the full version, your account would be created.');
        closeModal('registerModal');
    });
});

// Close modals when clicking outside
window.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});
