import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import EmptyState from "../components/EmptyState";

export default function Home() {
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);

  async function loadProcesses() {
    try {
      const res = await api.get("/processes/");
      setProcesses(res.data);
    } finally {
      setLoading(false);
    }
  }

  async function deleteProcess(id) {
    await api.delete(`/processes/${id}`);
    loadProcesses();
  }

  useEffect(() => {
    loadProcesses();
  }, []);

  return (
    <div className="grid">
      <section className="card hero-card">
        <h2 className="page-title">Mapeie processos com visão operacional e analítica</h2>
        <p className="page-subtitle">
          Cadastre fluxos, identifique gargalos, destaque desperdícios Lean e gere sugestões iniciais de To Be com apoio analítico.
        </p>
        <div className="inline-actions">
          <Link className="link-button" to="/novo-processo">
            Criar novo processo
          </Link>
        </div>
      </section>

      <section>
        <h2 className="page-title">Seus processos</h2>
        <p className="page-subtitle">
          Visualize os processos cadastrados e acesse rapidamente o diagnóstico do estado atual.
        </p>
      </section>

      {loading ? (
        <p>Carregando processos...</p>
      ) : processes.length === 0 ? (
        <EmptyState
          title="Nenhum processo cadastrado"
          description="Crie seu primeiro processo para começar a mapear o fluxo atual, analisar gargalos e gerar sugestões de melhoria."
        />
      ) : (
        <div className="grid grid-2">
          {processes.map((process) => (
            <div className="card" key={process.id}>
              <h3>{process.name}</h3>
              <p><strong>Área:</strong> {process.area || "-"}</p>
              <p><strong>Cliente:</strong> {process.customer || "-"}</p>
              <p className="muted">{process.objective || "Sem objetivo informado."}</p>

              <div className="inline-actions">
                <Link className="link-button" to={`/processo/${process.id}`}>
                  Abrir processo
                </Link>
                <Link className="link-button" to={`/diagnostico/${process.id}`}>
                  Ver diagnóstico
                </Link>
                <button className="danger" onClick={() => deleteProcess(process.id)}>
                  Excluir
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
