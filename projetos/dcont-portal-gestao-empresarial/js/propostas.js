import { db } from "./firebase-config.js";
import { collection, addDoc, doc, getDoc, updateDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const { jsPDF } = window.jspdf;
const params = new URLSearchParams(window.location.search);
const leadId = params.get("lead");

window.gerarProposta = async function(){

  const valor = Number(document.getElementById("valor").value);

  const propostaRef = await addDoc(collection(db,"propostas"),{
    leadId,
    valor,
    status:"enviada",
    createdAt:new Date()
  });

  // PDF
  const pdf = new jsPDF();
  pdf.text("Proposta Comercial",20,20);
  pdf.text("Valor: R$ "+valor,20,40);
  pdf.save("proposta.pdf");

};

const { jsPDF } = window.jspdf;

function exportarDRE(receita,despesa,resultado){

  const pdf = new jsPDF();

  pdf.text("DRE - Demonstrativo de Resultado",20,20);
  pdf.text("Receita: "+receita,20,40);
  pdf.text("Despesa: "+despesa,20,50);
  pdf.text("Resultado: "+resultado,20,60);

  pdf.save("DRE.pdf");
};

window.aceitarProposta = async function(id){

  await updateDoc(doc(db,"propostas",id),{
    status:"aceita"
  });

  await addDoc(collection(db,"projects"),{
    propostaId:id,
    status:"planejamento",
    createdAt:new Date()
  });

};

