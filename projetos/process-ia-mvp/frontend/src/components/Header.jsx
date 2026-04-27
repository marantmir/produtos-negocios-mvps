import { Link } from "react-router-dom";

export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <div>
          <h1 className="brand-title">Process IA MVP</h1>
          <p className="brand-subtitle">Mapeamento de processos, análise As Is e sugestões To Be</p>
        </div>

        <nav className="nav-links">
          <Link to="/">Início</Link>
          <Link to="/novo-processo">Novo Processo</Link>
        </nav>
      </div>
    </header>
  );
}
