import { db } from "./firebase.js";
import {
  addDoc,
  collection,
  serverTimestamp
} from "https://www.gstatic.com/firebasejs/10.14.0/firebase-firestore.js";
import { auth } from "./firebase.js";
import { onAuthStateChanged } from "https://www.gstatic.com/firebasejs/10.14.0/firebase-auth.js";

const contactForm = document.getElementById("contactForm");
const messageDiv = document.getElementById("contactMessage");
const contactBtn = document.getElementById("contactBtn");

if (contactForm) {
  contactForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value.trim();
    const email = document.getElementById("email").value.trim();
    const subject = document.getElementById("subject").value.trim();
    const message = document.getElementById("message").value.trim();

    if (!name || !email || !subject || !message) {
      showStatus("❌ Please fill out all fields.", "error");
      return;
    }

    contactBtn.disabled = true;
    contactBtn.textContent = "Sending...";

    try {
      await addDoc(collection(db, "contactMessages"), {
        name,
        email,
        subject,
        message,
        createdAt: serverTimestamp(),
      });

      showStatus("✅ Message sent successfully!", "success");
      contactForm.reset();
    } catch (error) {
      console.error("❌ Firestore Error:", error);
      showStatus("❌ Failed to send message. Please try again.", "error");
    } finally {
      contactBtn.disabled = false;
      contactBtn.textContent = "Send Message";
    }
  });
}

function showStatus(text, type) {
  messageDiv.innerHTML = `
    <div class="contact-result-card ${type}">
      <div class="contact-result-title">${type === "success" ? "Message Sent" : "Error"}</div>
      <div class="contact-result-message">${text}</div>
    </div>
  `;
  messageDiv.classList.add("show");
}

// Check authentication and show navbar
document.addEventListener('DOMContentLoaded', async function() {
    const isLoggedIn = await window.authManager.checkAuth();
    if (!isLoggedIn) {
        // Redirect to login if not authenticated
        window.location.href = '/login.html';
        return;
    }
    // Show navbar and update buttons
    await window.authManager.updateNavbar();
});

onAuthStateChanged(auth, (user) => {
  if (user && document.getElementById("email")) {
    document.getElementById("email").value = user.email;
  }
});
