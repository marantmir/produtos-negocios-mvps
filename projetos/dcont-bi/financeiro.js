import { db } from "./firebase-config.js";
import { collection, addDoc, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

window.addReceita = async () => {
    const valor = prompt("Valor da Receita:");
    if (!valor) return;

    await addDoc(collection(db, "financeiro"), {
        tipo: "receita" | "despesa",
		categoria: "imposto" | "honorario" | "software" | "marketing",
        valor: Number(valor),
        data: new Date()
    });

    alert("Receita adicionada!");
    loadFinanceiro();
};

window.loadFinanceiro = async () => {
    const snapshot = await getDocs(collection(db, "financeiro"));
    let receita = 0;

    snapshot.forEach(doc => {
        const d = doc.data();
        if (d.tipo === "receita") receita += d.valor;
    });

    document.getElementById("receita").innerText = "R$ " + receita.toFixed(2);
};

loadFinanceiro();
