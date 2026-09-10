import { NavLink, Route, Routes } from "react-router-dom";
import Catalogo from "./pages/Catalogo";
import Movimientos from "./pages/Movimientos";
import Precios from "./pages/Precios";
import Resumen from "./pages/Resumen";

const link = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium ${
    isActive ? "bg-white text-ink" : "text-paper/90 hover:bg-white/15"
  }`;

export default function App() {
  return (
    <div className="min-h-screen">
      <header className="bg-rust text-paper shadow-md">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3">
          <h1 className="font-display text-2xl tracking-wide">ACCIONES</h1>
          <nav className="flex flex-wrap gap-1">
            <NavLink to="/" className={link} end>
              Resumen
            </NavLink>
            <NavLink to="/precios" className={link}>
              Precios
            </NavLink>
            <NavLink to="/movimientos" className={link}>
              Movimientos
            </NavLink>
            <NavLink to="/catalogo" className={link}>
              Catálogo
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Routes>
          <Route path="/" element={<Resumen />} />
          <Route path="/precios" element={<Precios />} />
          <Route path="/movimientos" element={<Movimientos />} />
          <Route path="/catalogo" element={<Catalogo />} />
        </Routes>
      </main>
    </div>
  );
}
