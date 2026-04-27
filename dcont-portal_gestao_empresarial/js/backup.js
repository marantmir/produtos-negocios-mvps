async function exportarJSON(){

  const snap = await getDocs(collection(db,"financeiro"));

  let dados=[];
  snap.forEach(doc=>{
    dados.push(doc.data());
  });

  const blob = new Blob([JSON.stringify(dados)], {type:"application/json"});
  const url = URL.createObjectURL(blob);

  const a=document.createElement("a");
  a.href=url;
  a.download="backup.json";
  a.click();
}
