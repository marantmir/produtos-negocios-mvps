import { db } from "./firebase-config.js";
import { collection, addDoc, getDocs } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

window.addProject = async () => {
    const nome = prompt("Nome do Projeto:");
    if (!nome) return;

    await addDoc(collection(db, "projects"), {
        nomeProjeto: nome,
        status: "em andamento",
        inicio: new Date()
    });

    alert("Projeto criado!");
};
