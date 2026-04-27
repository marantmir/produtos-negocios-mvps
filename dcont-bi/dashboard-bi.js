import { db } from "./firebase-config.js";
import { collection, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

async function gerarDashboardBI() {

    const leadsSnap = await getDocs(collection(db, "leads"));
    const financeiroSnap = await getDocs(collection(db, "financeiro"));

    let totalLeads = 0;
    let fechados = 0;
    let receita = 0;
    let despesas = 0;

    const statusCount = {
        novo: 0,
        contatado: 0,
        proposta: 0,
        fechado: 0,
        perdido: 0
    };

    leadsSnap.forEach(doc => {
        totalLeads++;
        const data = doc.data();
        statusCount[data.status]++;

        if (data.status === "fechado")
            fechados++;
    });

    financeiroSnap.forEach(doc => {
        const f = doc.data();
        if (f.tipo === "receita") receita += f.valor;
        if (f.tipo === "despesa") despesas += f.valor;
    });

    const lucro = receita - despesas;
    const conversao = totalLeads > 0 ? (fechados / totalLeads) * 100 : 0;
    const ticketMedio = fechados > 0 ? receita / fechados : 0;

    // =========================
    // FUNIL
    // =========================
    new Chart(document.getElementById("graficoFunil"), {
        type: "bar",
        data: {
            labels: Object.keys(statusCount),
            datasets: [{
                label: "Leads",
                data: Object.values(statusCount)
            }]
        }
    });

    // =========================
    // RECEITA X DESPESA
    // =========================
    new Chart(document.getElementById("graficoFinanceiro"), {
        type: "bar",
        data: {
            labels: ["Receita", "Despesa", "Lucro"],
            datasets: [{
                label: "Financeiro",
                data: [receita, despesas, lucro]
            }]
        }
    });

    // =========================
    // DRE AUTOMÁTICA
    // =========================
    document.getElementById("dreResumo").innerHTML = `
        <p><strong>Receita Bruta:</strong> R$ ${receita.toFixed(2)}</p>
        <p><strong>Despesas:</strong> R$ ${despesas.toFixed(2)}</p>
        <hr>
        <p><strong>Lucro Operacional:</strong> R$ ${lucro.toFixed(2)}</p>
        <hr>
        <p><strong>Conversão:</strong> ${conversao.toFixed(2)}%</p>
        <p><strong>Ticket Médio:</strong> R$ ${ticketMedio.toFixed(2)}</p>
    `;
}

gerarDashboardBI();
