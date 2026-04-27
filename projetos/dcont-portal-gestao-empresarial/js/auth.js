import { auth, db } from "./firebase-config.js";
import { doc, getDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

auth.onAuthStateChanged(async user=>{
  if(user){
    const snap = await getDoc(doc(db,"usuarios",user.uid));
    const role = snap.data().role;

    if(role==="cliente"){
      window.location="cliente.html";
    }
  }
});
