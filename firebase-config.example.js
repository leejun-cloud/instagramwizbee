// =============================================================================
// Firebase Web Config — EXAMPLE / TEMPLATE
// =============================================================================
// HOW TO USE:
//   1. Copy this file to `firebase-config.js` (in the same directory).
//   2. Replace the placeholder values with your real Firebase Web App config.
//   3. `firebase-config.js` is gitignored — your API key will never be committed.
//
//   You can find the real values in Firebase Console → Project Settings →
//   General → Your apps → Web app → "SDK setup and configuration".
// =============================================================================

export const firebaseConfig = {
    projectId: "YOUR_PROJECT_ID",
    appId: "YOUR_APP_ID",
    apiKey: "YOUR_FIREBASE_WEB_API_KEY",
    authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
    databaseURL: "https://YOUR_PROJECT_ID-default-rtdb.firebaseio.com",
    storageBucket: "YOUR_PROJECT_ID.firebasestorage.app",
    messagingSenderId: "YOUR_SENDER_ID"
};
