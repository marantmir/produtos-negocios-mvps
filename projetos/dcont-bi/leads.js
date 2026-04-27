import { db } from "./firebase-config.js";
import { 
  collection, 
  getDocs, 
  updateDoc, 
  doc, 
  addDoc 
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

window.loadLeads = async () => {
    const snapshot = await getDocs(collection(db, "leads"));
    const tbody = document.getElementById("leadsTable");
    tbody.innerHTML = "";

    snapshot.forEach((docSnap) => {
        const data = docSnap.data();

        tbody.innerHTML += `
        <tr>
            <td>${data.nome}</td>
            <td>${data.email}</td>
            <td>
                <select onchange="updateStatus('${docSnap.id}', this.value)">
                    <option ${data.status==='novo'?'selected':''}>novo</option>
                    <option ${data.status==='contatado'?'selected':''}>contatado</option>
                    <option ${data.status==='proposta'?'selected':''}>proposta</option>
                    <option ${data.status==='fechado'?'selected':''}>fechado</option>
                    <option ${data.status==='perdido'?'selected':''}>perdido</option>
                </select>
            </td>
            <td>${data.valorProposta || 0}</td>
        </tr>
        `;
    });
};

window.updateStatus = async (id, status) => {

    await updateDoc(doc(db, "leads", id), { 
        status,
        updatedAt: new Date()
    });

    // Registrar histórico
    await addDoc(collection(db, "history"), {
        entidade: "lead",
        entidadeId: id,
        acao: "Status alterado para " + status,
        data: new Date()
    });
};
