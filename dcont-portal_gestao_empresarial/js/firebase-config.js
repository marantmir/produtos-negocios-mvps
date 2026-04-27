import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

const firebaseConfig = {
  apiKey: "AIzaSyDtRTKhlogKi9DGp_7kRWDVkeLFzAWMHek",
  authDomain: "dcont-portal.firebaseapp.com",
  projectId: "dcont-portal",
  storageBucket: "dcont-portal.firebasestorage.app",
  messagingSenderId: "440147165990",
  appId: "1:440147165990:web:32370de307654bb61db7e7",
  measurementId: "G-9SEK71JHJ7"
};

const app = initializeApp(firebaseConfig);

export const db = getFirestore(app);
export const auth = getAuth(app);
