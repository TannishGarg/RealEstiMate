// Authentication and Navigation Management
// Define API_BASE_URL (use var to allow redeclaration)
var API_BASE_URL = window.API_BASE_URL || 'http://localhost:5000/api';
window.API_BASE_URL = API_BASE_URL;

// Check authentication status
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/check-auth`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            return false;
        }
        const data = await response.json();
        return data.logged_in || false;
    } catch (error) {
        console.error('Error checking auth:', error);
        return false;
    }
}

// Update navbar visibility based on login status
async function updateNavbar() {
    const navbar = document.querySelector('.navbar');
    const isLoggedIn = await checkAuth();
    const currentPage = window.location.pathname;
    
    if (navbar) {
        // Hide navbar on home page even if logged in
        if (isLoggedIn && !currentPage.includes('index.html') && currentPage !== '/') {
            navbar.style.display = 'block';
            updateNavbarButtons(isLoggedIn);
        } else {
            navbar.style.display = 'none';
        }
    }
}

// Update navbar buttons (Login/Logout)
function updateNavbarButtons(isLoggedIn) {
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;
    
    // Remove existing login/logout buttons
    const existingAuthBtn = navLinks.querySelector('.auth-btn');
    if (existingAuthBtn) {
        existingAuthBtn.remove();
    }
    
    // Create new button based on login status
    const authBtn = document.createElement('li');
    if (isLoggedIn) {
        authBtn.innerHTML = '<a href="#" class="btn btn-secondary logout-btn">Logout</a>';
        authBtn.querySelector('.logout-btn').addEventListener('click', handleLogout);
    } else {
        authBtn.innerHTML = '<a href="/login.html" class="btn btn-secondary">Login</a>';
    }
    authBtn.classList.add('auth-btn');
    navLinks.appendChild(authBtn);
}

// Handle login
async function handleLogin(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Login error:', error);
        return { success: false, error: 'Network error' };
    }
}

// Handle logout
async function handleLogout(e) {
    if (e) e.preventDefault();
    
    try {
        const response = await fetch(`${API_BASE_URL}/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });
        
        const data = await response.json();
        if (data.success) {
            // Update navbar
            await updateNavbar();
            // Redirect to home page
            window.location.href = '/';
        }
    } catch (error) {
        console.error('Logout error:', error);
        // Still redirect even if API call fails
        window.location.href = '/';
    }
}

// Export functions for use in other scripts
window.authManager = {
    checkAuth,
    handleLogin,
    handleLogout,
    updateNavbar
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateNavbar();
    
    // Set up logout button if it exists
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

