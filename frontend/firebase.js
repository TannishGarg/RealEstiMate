// firebase.js

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.0/firebase-app.js";
import {
  getAuth,
  setPersistence,
  browserLocalPersistence,
  onAuthStateChanged,
  signOut
} from "https://www.gstatic.com/firebasejs/10.14.0/firebase-auth.js";
import {
  getFirestore,
  serverTimestamp
} from "https://www.gstatic.com/firebasejs/10.14.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyAZ_pjoGEBjA8h-bkbwwG4u63NrFFW2Ghc",
  authDomain: "indian-house01.firebaseapp.com",
  projectId: "indian-house01",
  storageBucket: "indian-house01.firebasestorage.app",
  messagingSenderId: "1061781916538",
  appId: "1:1061781916538:web:617b50ead70ecd2455e4c3",
  measurementId: "G-HCLY5Y9X22"
};

// Initialize Firebase
export const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
export const now = serverTimestamp;

// Keep user logged in after refresh
await setPersistence(auth, browserLocalPersistence);

// Protect pages that require authentication
export function guardPage(requireLogin = false, redirect = "login.html") {
  onAuthStateChanged(auth, (user) => {
    if (requireLogin && !user) {
      window.location.href = redirect;
    }
  });
}

// Logout function
export async function logout() {
  await signOut(auth);
  window.location.href = "login.html";
}
