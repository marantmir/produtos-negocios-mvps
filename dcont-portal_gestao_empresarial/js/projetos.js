import { db } from "./firebase-config.js";
import { collection, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

async function calcularMargemProjeto(projectId){

  const snap = await getDocs(collection(db,"financeiro"));

  let receita=0, custo=0;

  snap.forEach(doc=>{
    const f = doc.data();
    if(f.projetoId === projectId){
      if(f.tipo==="receita") receita+=f.valor;
      if(f.tipo==="despesa") custo+=f.valor;
    }
  });

  const margem = ((receita-custo)/receita)*100;

  return margem.toFixed(2);
}
