import { db } from "./firebase-config.js";
import { collection, getDocs, addDoc } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

window.gerarRelatorioMensal = async () => {

    const leadsSnapshot = await getDocs(collection(db, "leads"));
    const financeiroSnapshot = await getDocs(collection(db, "financeiro"));

    let total = 0;
    let fechados = 0;
    let receita = 0;

    leadsSnapshot.forEach(doc => {
        total++;
        if (doc.data().status === "fechado") fechados++;
    });

    financeiroSnapshot.forEach(doc => {
        if (doc.data().tipo === "receita")
            receita += doc.data().valor;
    });

    const conversao = total > 0 ? (fechados / total) * 100 : 0;

    await addDoc(collection(db, "reports"), {
        tipo: "mensal",
        periodo: new Date().toISOString().slice(0,7),
        totalLeads: total,
        totalFechados: fechados,
        receita,
        conversao,
        criadoEm: new Date()
    });

    alert("Relatório mensal gerado!");
};

