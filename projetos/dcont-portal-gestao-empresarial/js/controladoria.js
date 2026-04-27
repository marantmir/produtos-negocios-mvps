import { db } from "./firebase-config.js";
import { collection, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

async function gerarDRE(){

  const snap = await getDocs(collection(db,"financeiro"));

  let receita=0, despesa=0;

  snap.forEach(doc=>{
    if(doc.data().tipo==="receita") receita+=doc.data().valor;
    if(doc.data().tipo==="despesa") despesa+=doc.data().valor;
  });

  resultado.innerText = receita-despesa;
}

gerarDRE();
