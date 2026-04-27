import { db } from "./firebase-config.js";
import { collection, addDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

window.salvarFinanceiro = async function(){

  await addDoc(collection(db,"financeiro"),{
    tipo: tipo.value,
    valor: Number(valor.value),
    competencia: competencia.value,
    createdAt:new Date()
  });

};
