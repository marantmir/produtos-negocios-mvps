// firebase-config.js
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyDtRTKhlogKi9DGp_7kRWDVkeLFzAWMHek",
  authDomain: "dcont-portal.firebaseapp.com",
  projectId: "dcont-portal",
  storageBucket: "dcont-portal.firebasestorage.app",
  messagingSenderId: "440147165990",
  appId: "1:440147165990:web:394c17b1aac05fb41db7e7",
  measurementId: "G-6N4XZ0Y13E"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
