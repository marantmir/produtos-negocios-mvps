import { useState } from "react";
import api from "../api/client";

export default function NewProcessForm() {
  const [form, setForm] = useState({
    name: "",
    area: "",
    objective: "",
    customer: "",
    start_event: "",
    end_event: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function onChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!form.name.trim()) {
      setError("Informe o nome do processo.");
      return;
    }

    setLoading(true);

    try {
      await api.post("/processes/", {
        ...form,
        name: form.name.trim(),
        area: form.area.trim(),
        objective: form.objective.trim(),
        customer: form.customer.trim(),
        start_event: form.start_event.trim(),
        end_event: form.end_event.trim(),
      });

      setSuccess("Processo criado com sucesso.");
      setForm({
        name: "",
        area: "",
        objective: "",
        customer: "",
        start_event: "",
        end_event: "",
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <input
        name="name"
        value={form.name}
        onChange={onChange}
        placeholder="Nome do processo"
        required
      />

      <input
        name="area"
        value={form.area}
        onChange={onChange}
        placeholder="Área"
      />

      <textarea
        name="objective"
        value={form.objective}
        onChange={onChange}
        placeholder="Objetivo do processo"
      />

      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}
      {success && <p style={{ color: "#166534" }}>{success}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Salvando..." : "Salvar processo"}
      </button>
    </form>
  );
}
