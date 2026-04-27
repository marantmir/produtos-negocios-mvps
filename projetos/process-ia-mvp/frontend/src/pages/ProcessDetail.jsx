import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api";
import StepCard from "../components/StepCard";
import EmptyState from "../components/EmptyState";

const initialStep = {
  step_name: "",
  step_order: 1,
  owner: "",
  execution_time: 0,
  waiting_time: 0,
  adds_value: true,
  has_rework: false,
  approvals: 0,
  notes: "",
};

export default function ProcessDetail() {
  const { id } = useParams();
  const [process, setProcess] = useState(null);
  const [step, setStep] = useState(initialStep);

  async function loadProcess() {
    const res = await api.get(`/processes/${id}`);
    setProcess(res.data);
  }

  useEffect(() => {
    loadProcess();
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    await api.post(`/processes/${id}/steps`, {
      ...step,
      step_order: Number(step.step_order),
      execution_time: Number(step.execution_time),
      waiting_time: Number(step.waiting_time),
      approvals: Number(step.approvals),
    });
    
    setStep({
      ...initialStep,
      step_order: process?.steps?.length ? process.steps.length + 1 : 1,
    });

    loadProcess();
  };

  const handleDeleteStep = async (stepId) => {
    await api.delete(`/processes/steps/${stepId}`);
    loadProcess();
  };
  
  if (!process) return <p>Carregando processo...</p>;

  return (
    <div className="grid">
      <div className="card">
        <h2 className="page-title">{process.name}</h2>
        <p><strong>Área:</strong> {process.area || "-"}</p>
        <p><strong>Cliente:</strong> {process.customer || "-"}</p>
        <p><strong>Evento inicial:</strong> {process.start_event || "-"}</p>
        <p><strong>Evento final:</strong> {process.end_event || "-"}</p>
        <p><strong>Objetivo:</strong> {process.objective || "-"}</p>

        <div className="inline-actions">
          <Link className="link-button" to={`/diagnostico/${process.id}`}>
            Ver diagnóstico As Is
          </Link>
        </div>
      </div>
      
      <div className="card">
        <h3>Adicionar etapa do processo</h3>
        <form className="form-grid" onSubmit={handleSubmit}>
          <input
            placeholder="Nome da etapa"
            value={step.step_name}
            onChange={(e) => setStep({ ...step, step_name: e.target.value })}
            required
          />

          <input
            type="number"
            min="1"
            placeholder="Ordem da etapa"
            value={step.step_order}
            onChange={(e) => setStep({ ...step, step_order: e.target.value })}
            required
          />
          
          <input
            placeholder="Responsável"
            value={step.owner}
            onChange={(e) => setStep({ ...step, owner: e.target.value })}
          />

          <input
            type="number"
            min="0"
            step="0.1"
            placeholder="Tempo de execução"
            value={step.execution_time}
            onChange={(e) => setStep({ ...step, execution_time: e.target.value })}
          />

          <input
            type="number"
            min="0"
            step="0.1"
            placeholder="Tempo de espera"
            value={step.waiting_time}
            onChange={(e) => setStep({ ...step, waiting_time: e.target.value })}
          />
          
          <input
            type="number"
            min="0"
            placeholder="Quantidade de aprovações"
            value={step.approvals}
            onChange={(e) => setStep({ ...step, approvals: e.target.value })}
          />

          <div className="checkbox-row">
            <label>
              <input
                type="checkbox"
                checked={step.adds_value}
                onChange={(e) => setStep({ ...step, adds_value: e.target.checked })}
              />
              Agrega valor
            </label>
            
            <label>
              <input
                type="checkbox"
                checked={step.has_rework}
                onChange={(e) => setStep({ ...step, has_rework: e.target.checked })}
              />
              Tem retrabalho
            </label>
          </div>

          <textarea
            placeholder="Observações sobre a etapa"
            value={step.notes}
            onChange={(e) => setStep({ ...step, notes: e.target.value })}
          />

          <button type="submit">Adicionar etapa</button>
        </form>
      </div>
      
      <div className="card">
        <h3>Etapas cadastradas</h3>
        {process.steps.length === 0 ? (
          <EmptyState
            title="Nenhuma etapa cadastrada"
            description="Adicione as etapas do fluxo atual para permitir a análise As Is e a geração de sugestões de melhoria."
          />
        ) : (
          <div className="grid">
            {process.steps
              .slice()
              .sort((a, b) => a.step_order - b.step_order)
              .map((s) => (
                <StepCard key={s.id} step={s} onDelete={handleDeleteStep} />
              ))}
          </div>
        )}
      </div>
    </div>
  );
}
