// ✅ Combined Firebase Authentication + Navbar Management
// (Keeps old functionality + integrates Firebase logic)

// Import Firebase core setup
import { auth } from "./firebase.js";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  setPersistence,
  browserLocalPersistence,
  GoogleAuthProvider,
  signInWithPopup
} from "https://www.gstatic.com/firebasejs/10.14.0/firebase-auth.js";

// ------------------------------
// 🔹 Keep users logged in locally
// ------------------------------
await setPersistence(auth, browserLocalPersistence);
console.log("✅ Firebase Auth initialized and persistent!");

// ------------------------------
// 🔹 Check Authentication Status
// ------------------------------
async function checkAuth() {
  return new Promise((resolve) => {
    onAuthStateChanged(auth, (user) => {
      resolve(!!user);
    });
  });
}

// ------------------------------
// 🔹 Modern Notification System
// ------------------------------
function showNotification(message, type = 'success') {
  // Remove any existing notifications
  const existingNotification = document.querySelector('.notification');
  if (existingNotification) {
    existingNotification.remove();
  }

  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;

  // Add to page
  document.body.appendChild(notification);

  // Auto-remove after animation completes (2 seconds total)
  setTimeout(() => {
    if (notification.parentNode) {
      notification.remove();
    }
  }, 2000);
}

// ------------------------------
// 🔹 Update Hero Buttons (Get Started -> Start Predicting)
// ------------------------------
function updateHeroButtons(isLoggedIn) {
  const heroButtons = document.getElementById("heroButtons");
  if (!heroButtons) return;

  const getStartedBtn = heroButtons.querySelector(".btn-primary-modern");
  if (getStartedBtn) {
    if (isLoggedIn) {
      getStartedBtn.textContent = "Start Predicting";
      getStartedBtn.href = "/prediction.html";
    } else {
      getStartedBtn.textContent = "Get Started";
      getStartedBtn.href = "/login.html";
    }
  }
}

// ------------------------------
// 🔹 Navbar Visibility Management
// ------------------------------
async function updateNavbar() {
  const navbar = document.querySelector(".navbar");
  const navLinks = document.querySelector(".nav-links");
  if (!navbar || !navLinks) return;

  const isLoggedIn = await checkAuth();
  const currentPage = window.location.pathname;

  // Hide navbar on home page (index.html or /)
  if (isLoggedIn && !currentPage.includes("index.html") && currentPage !== "/") {
    navbar.style.display = "block";
    updateNavbarButtons(isLoggedIn);
    
    // Add slide-down animation for pages with navbar
    if (currentPage.includes("prediction.html") || 
        currentPage.includes("about.html") || 
        currentPage.includes("contact.html") || 
        currentPage.includes("signup.html") || 
        currentPage.includes("login.html")) {
      navbar.classList.add("navbar-animate-down");
      // Remove animation class after animation completes to allow re-triggering
      setTimeout(() => {
        navbar.classList.remove("navbar-animate-down");
      }, 800);
    }
  } else if (!isLoggedIn && !currentPage.includes("index.html") && currentPage !== "/") {
    navbar.style.display = "block";
    updateNavbarButtons(isLoggedIn);
    
    // Add slide-down animation for pages with navbar
    if (currentPage.includes("prediction.html") || 
        currentPage.includes("about.html") || 
        currentPage.includes("contact.html") || 
        currentPage.includes("signup.html") || 
        currentPage.includes("login.html")) {
      navbar.classList.add("navbar-animate-down");
      // Remove animation class after animation completes to allow re-triggering
      setTimeout(() => {
        navbar.classList.remove("navbar-animate-down");
      }, 800);
    }
  } else {
    navbar.style.display = "none";
  }

  // Update hero buttons on home page
  if (currentPage.includes("index.html") || currentPage === "/") {
    updateHeroButtons(isLoggedIn);
  }

  // Ensure "RealEstiMate" logo navigates home without logout
  const logo = document.querySelector(".logo a");
  if (logo) {
    logo.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.href = "/index.html";
    });
  }
}

// ------------------------------
// 🔹 Update Navbar Buttons
// ------------------------------
function updateNavbarButtons(isLoggedIn) {
  const navLinks = document.querySelector(".nav-links");
  if (!navLinks) return;

  // Remove existing Login/Logout button
  const existingAuthBtn = navLinks.querySelector(".auth-btn");
  if (existingAuthBtn) existingAuthBtn.remove();

  // Create new button
  const authBtn = document.createElement("li");
  authBtn.classList.add("auth-btn");

  if (isLoggedIn) {
    authBtn.innerHTML = '<a href="#" class="btn btn-secondary logout-btn">Logout</a>';
    authBtn.querySelector(".logout-btn").addEventListener("click", handleLogout);
  } else {
    authBtn.innerHTML = '<a href="/login.html" class="btn btn-secondary">Login</a>';
  }

  navLinks.appendChild(authBtn);
}

// ------------------------------
// 🔹 Signup Form
// ------------------------------
const signupForm = document.getElementById("signupForm");
if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("suEmail").value.trim();
    const password = document.getElementById("suPassword").value.trim();
    const errorBox = document.getElementById("suError");

    try {
      console.log("🔐 Attempting signup for:", email);
      await createUserWithEmailAndPassword(auth, email, password);
      
      // Show modern success notification
      showNotification("Signup successful! Redirecting to login...", "success");
      
      // Redirect after delay
      setTimeout(() => {
        window.location.href = "login.html";
      }, 2000);
    } catch (err) {
      console.error("❌ Signup error:", err.code, err.message);
      switch (err.code) {
        case "auth/email-already-in-use":
          errorBox.textContent = "❌ This email is already registered. Please login instead.";
          break;
        case "auth/invalid-email":
          errorBox.textContent = "❌ Invalid email format. Please enter a valid email.";
          break;
        case "auth/weak-password":
          errorBox.textContent = "❌ Password is too weak. Please use at least 6 characters.";
          break;
        default:
          errorBox.textContent = `❌ Signup failed: ${err.message}`;
      }
    }
  });
}

// ------------------------------
// 🔹 Login Form
// ------------------------------
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("liEmail").value.trim();
    const password = document.getElementById("liPassword").value.trim();
    const errorBox = document.getElementById("liError");

    try {
      console.log("🔐 Attempting login with:", email);
      await signInWithEmailAndPassword(auth, email, password);
      
      // Show modern success notification
      showNotification("Login successful! Redirecting to prediction page...", "success");
      
      // Redirect after delay
      setTimeout(() => {
        window.location.href = "prediction.html";
      }, 2000);
    } catch (err) {
      console.error("❌ Login error:", err.code, err.message);
      errorBox.style.display = "block";
      errorBox.style.color = "#ff6b6b";
      errorBox.style.fontWeight = "500";
      errorBox.style.textAlign = "center";
      errorBox.style.marginTop = "10px";
      errorBox.style.fontSize = "14px";
      errorBox.textContent = "❌ Invalid email or password. Please check your credentials and try again.";
    }
  });
}

// ------------------------------
// 🔹 Logout Handler
// ------------------------------
async function handleLogout(e) {
  if (e) e.preventDefault();
  try {
    await signOut(auth);
    console.log("👋 Logged out successfully!");
    await updateNavbar();
    window.location.href = "/index.html"; // redirect home
  } catch (error) {
    console.error("Logout error:", error);
    window.location.href = "/index.html";
  }
}

// ------------------------------
// 🔹 Google Auth (Login + Signup)
// ------------------------------
const provider = new GoogleAuthProvider();

// Google Login
const googleLoginBtn = document.getElementById("googleLoginBtn");
if (googleLoginBtn) {
  googleLoginBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    try {
      await signInWithPopup(auth, provider);
      showNotification("✅ Logged in with Google! Redirecting...", "success");
      setTimeout(() => (window.location.href = "prediction.html"), 1500);
    } catch (error) {
      console.error("Google login error:", error);
      alert("❌ Google Sign-In failed: " + error.message);
    }
  });
}

// Google Signup
const googleSignupBtn = document.getElementById("googleSignupBtn");
if (googleSignupBtn) {
  googleSignupBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    try {
      await signInWithPopup(auth, provider);
      showNotification("✅ Account created with Google! Redirecting...", "success");
      setTimeout(() => (window.location.href = "prediction.html"), 1500);
    } catch (error) {
      console.error("Google signup error:", error);
      alert("❌ Google Sign-Up failed: " + error.message);
    }
  });
}

// ------------------------------
// 🔹 Listen for Auth Changes
// ------------------------------
onAuthStateChanged(auth, (user) => {
  updateNavbarButtons(!!user);
  updateNavbar();
});

// ------------------------------
// 🔹 Exports (for external scripts)
// ------------------------------
window.authManager = {
  checkAuth,
  updateNavbar,
  updateHeroButtons,
  handleLogout,
  showNotification
};

// ------------------------------
// 🔹 Initialize Navbar on Page Load
// ------------------------------
document.addEventListener("DOMContentLoaded", () => {
  updateNavbar();
});
