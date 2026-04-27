import { Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Home from "./pages/Home";
import NewProcess from "./pages/NewProcess";
import ProcessDetail from "./pages/ProcessDetail";
import DiagnosticView from "./pages/DiagnosticView";

export default function App() {
  return (
    <div className="app-shell">
      <Header />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/novo-processo" element={<NewProcess />} />
          <Route path="/processo/:id" element={<ProcessDetail />} />
          <Route path="/diagnostico/:id" element={<DiagnosticView />} />
        </Routes>
      </main>
    </div>
  );
}
