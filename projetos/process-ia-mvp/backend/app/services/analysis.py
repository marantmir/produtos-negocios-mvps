def generate_diagnostic(process):
    steps = sorted(process.steps, key=lambda s: s.step_order)

    execution_time_total = sum(step.execution_time for step in steps)
    waiting_time_total = sum(step.waiting_time for step in steps)
    lead_time_total = execution_time_total + waiting_time_total

    non_value_steps = sum(1 for step in steps if not step.adds_value)
    rework_steps = sum(1 for step in steps if step.has_rework)
    approval_points = sum(step.approvals for step in steps)

    bottlenecks = [
        step.step_name for step in steps
        if step.waiting_time >= 8 or step.execution_time >= 8
    ]

    lean_wastes = []
    if waiting_time_total > execution_time_total:
        lean_wastes.append("Espera excessiva")
    if non_value_steps > 0:
        lean_wastes.append("Atividades sem valor agregado")
    if rework_steps > 0:
        lean_wastes.append("Retrabalho")
    if approval_points >= 3:
        lean_wastes.append("Excesso de aprovações")

    recommendations = []
    if waiting_time_total > execution_time_total:
        recommendations.append("Reduzir filas e tempos de espera entre etapas.")
    if non_value_steps > 0:
        recommendations.append("Revisar ou eliminar etapas que não agregam valor ao cliente.")
    if rework_steps > 0:
        recommendations.append("Aplicar análise de causa raiz nas etapas com retrabalho.")
    if approval_points >= 3:
        recommendations.append("Avaliar simplificação do fluxo de aprovações.")
    if bottlenecks:
        recommendations.append("Atacar gargalos com redistribuição de carga, padronização ou automação.")

    return {
        "lead_time_total": round(lead_time_total, 2),
        "execution_time_total": round(execution_time_total, 2),
        "waiting_time_total": round(waiting_time_total, 2),
        "total_steps": len(steps),
        "non_value_steps": non_value_steps,
        "rework_steps": rework_steps,
        "approval_points": approval_points,
        "bottlenecks": bottlenecks,
        "lean_wastes": lean_wastes,
        "recommendations": recommendations,
    }
