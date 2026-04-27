import { db } from "./firebase-config.js";
import { collection, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

async function gerarDashboard(){

  const leads = await getDocs(collection(db,"leads"));
  const projetos = await getDocs(collection(db,"projects"));

  document.getElementById("kpiLeads").innerText = leads.size;
  document.getElementById("kpiProjetos").innerText = projetos.size;
}

gerarDashboard();
