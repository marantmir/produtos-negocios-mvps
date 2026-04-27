import { db } from "./firebase-config.js";
import { collection, addDoc, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const lista = document.getElementById("listaLeads");

window.salvarLead = async function() {

  await addDoc(collection(db,"leads"),{
    nome: nome.value,
    empresa: empresa.value,
    email: email.value,
    status: status.value,
    createdAt: new Date()
  });

  carregar();
};

async function carregar(){
  lista.innerHTML = "";
  const snap = await getDocs(collection(db,"leads"));
  snap.forEach(doc=>{
    const li = document.createElement("li");
    li.innerHTML = `
      ${doc.data().nome} - ${doc.data().status}
      <button onclick="window.location='propostas.html?lead=${doc.id}'">
      Gerar Proposta
      </button>
    `;
    lista.appendChild(li);
  });
}

carregar();
