window.salvarEvento = async function(){

  await addDoc(collection(db,"agenda"),{
    titulo: titulo.value,
    data: data.value,
    tipo: tipo.value,
    createdAt:new Date()
  });

};
