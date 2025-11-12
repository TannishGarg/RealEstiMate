// frontend/firebase.js

// Import Firebase core SDK and required services
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.0/firebase-app.js";
import {
  getAuth,
  setPersistence,
  browserLocalPersistence
} from "https://www.gstatic.com/firebasejs/10.14.0/firebase-auth.js";
import {
  getFirestore
} from "https://www.gstatic.com/firebasejs/10.14.0/firebase-firestore.js";

// ✅ Your Firebase configuration (from your console)
const firebaseConfig = {
  apiKey: "AIzaSyAZ_pjoGEBjA8h-bkbwwG4u63NrFFW2Ghc",
  authDomain: "indian-house01.firebaseapp.com",
  projectId: "indian-house01",
  storageBucket: "indian-house01.firebasestorage.app",
  messagingSenderId: "1061781916538",
  appId: "1:1061781916538:web:617b50ead70ecd2455e4c3",
  measurementId: "G-HCLY5Y9X22"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

// Keep users logged in locally
await setPersistence(auth, browserLocalPersistence);

console.log("✅ Firebase connected successfully!");
