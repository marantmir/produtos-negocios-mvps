import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api";

export default function DiagnosticView() {
  const { id } = useParams();
  const [diagnostic, setDiagnostic] = useState(null);
  const [process, setProcess] = useState(null);

  useEffect(() => {
    async function loadData() {
      const [diagRes, processRes] = await Promise.all([
        api.get(`/diagnostics/${id}`),
        api.get(`/processes/${id}`),
      ]);
      setDiagnostic(diagRes.data);
      setProcess(processRes.data);
    }

    loadData();
  }, [id]);

  if (!diagnostic || !process) return <p>Carregando diagnóstico...</p>;

  return (
    <div className="grid">
      <section className="card hero-card">
        <h2 className="page-title">Diagnóstico As Is — {process.name}</h2>
        <p>
          Esta visão resume o comportamento atual do processo com base nas etapas cadastradas e nas regras analíticas do MVP.
        </p>
        <div className="inline-actions">
          <Link className="link-button" to={`/processo/${id}`}>
            Voltar ao processo
          </Link>
        </div>
      </section>

      <section className="card">
        <h3 className="section-title">Indicadores principais</h3>
        <div className="kpi-grid">
          <div className="kpi-box">
            <span className="kpi-label">Lead time total</span>
            <strong>{diagnostic.lead_time_total}</strong>
          </div>
          <div className="kpi-box">
            <span className="kpi-label">Execução total</span>
            <strong>{diagnostic.execution_time_total}</strong>
          </div>
          <div className="kpi-box">
            <span className="kpi-label">Espera total</span>
            <strong>{diagnostic.waiting_time_total}</strong>
          </div>
          <div className="kpi-box">
            <span className="kpi-label">Total de etapas</span>
            <strong>{diagnostic.total_steps}</strong>
          </div>
          <div className="kpi-box">
            <span className="kpi-label">Etapas sem valor</span>
            <strong>{diagnostic.non_value_steps}</strong>
          </div>
          <div className="kpi-box">
            <span className="kpi-label">Retrabalho</span>
            <strong>{diagnostic.rework_steps}</strong>
          </div>
          <div className="kpi-box">
            <span className="kpi-label">Pontos de aprovação</span>
            <strong>{diagnostic.approval_points}</strong>
          </div>
        </div>
      </section>

      <section className="card">
        <h3 className="section-title">Gargalos identificados</h3>
        {diagnostic.bottlenecks.length === 0 ? (
          <p className="muted">Nenhum gargalo crítico identificado pelas regras atuais do MVP.</p>
        ) : (
          <ul className="tag-list">
            {diagnostic.bottlenecks.map((item, index) => (
              <li className="tag" key={index}>{item}</li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h3 className="section-title">Desperdícios Lean</h3>
        {diagnostic.lean_wastes.length === 0 ? (
          <p className="muted">Nenhum desperdício crítico foi identificado pelas regras atuais.</p>
        ) : (
          <ul className="tag-list">
            {diagnostic.lean_wastes.map((item, index) => (
              <li className="tag" key={index}>{item}</li>
            ))}
          </ul>
        )}
      </section>

      <section className="card">
        <h3 className="section-title">Sugestões iniciais de To Be</h3>
        <ul className="list-clean">
          {diagnostic.recommendations.map((item, index) => (
            <li key={index} className="step-card">{item}</li>
          ))}
        </ul>
      </section>
    </div>
  );
}
