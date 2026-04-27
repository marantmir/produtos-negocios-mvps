export default function StepCard({ step, onDelete }) {
  return (
    <div className="step-card">
      <h4 className="step-title">
        {step.step_order}. {step.step_name}
      </h4>
      <p><strong>Responsável:</strong> {step.owner || "Não informado"}</p>
      <p><strong>Tempo de execução:</strong> {step.execution_time}</p>
      <p><strong>Tempo de espera:</strong> {step.waiting_time}</p>
      <p><strong>Aprovações:</strong> {step.approvals}</p>
      <p><strong>Agrega valor:</strong> {step.adds_value ? "Sim" : "Não"}</p>
      <p><strong>Retrabalho:</strong> {step.has_rework ? "Sim" : "Não"}</p>
      <p><strong>Observações:</strong> {step.notes || "-"}</p>

      <div className="inline-actions">
        <button className="danger" onClick={() => onDelete(step.id)}>
          Excluir etapa
        </button>
      </div>
    </div>
  );
}
