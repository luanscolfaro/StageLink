import { Link, useLocation, useNavigate } from "react-router-dom";
import { logout } from "../auth/auth";
import { Home, Search, User2, LogOut } from "lucide-react";
import Footer from "./Footer";

function Brand() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 14,
          background: "linear-gradient(135deg, var(--brand), var(--brand2))",
          display: "grid",
          placeItems: "center",
          color: "#06101b",
          fontWeight: 900,
          letterSpacing: "-0.04em",
          boxShadow: "0 20px 45px rgba(56,189,248,0.14)",
        }}
      >
        SL
      </div>
      <div>
        <div style={{ fontWeight: 800, letterSpacing: "-0.02em" }}>StageLink</div>
        <div style={{ fontSize: 12, color: "var(--muted)" }}>Link do palco</div>
      </div>
    </div>
    
  );
}

function NavItem({ to, icon: Icon, label }) {
  const location = useLocation();
  const active = location.pathname === to;

  return (
    <Link
      to={to}
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "11px 12px",
        borderRadius: 14,
        textDecoration: "none",
        background: active ? "rgba(56,189,248,0.14)" : "transparent",
        border: `1px solid ${active ? "rgba(56,189,248,0.35)" : "transparent"}`,
        color: "var(--text)",
      }}
    >
      <span
        style={{
          width: 36,
          height: 36,
          borderRadius: 14,
          display: "grid",
          placeItems: "center",
          border: "1px solid var(--border)",
          background: "rgba(255,255,255,0.04)",
        }}
      >
        <Icon size={18} />
      </span>
      <span style={{ fontWeight: 650 }}>{label}</span>
    </Link>
    
  );
}

export default function Layout({ children }) {
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="grid">
      <aside style={{ padding: 18, borderRight: "1px solid var(--border)", background: "rgba(0,0,0,0.10)" }}>
        <Brand />
        <div className="hr" />

        <div style={{ display: "grid", gap: 10 }}>
          <NavItem to="/feed" icon={Home} label="Feed" />
          <NavItem to="/gigs" icon={Search} label="Buscar vagas" />
          <NavItem to="/me" icon={User2} label="Perfil" />
        </div>

        <div style={{ marginTop: 18 }}>
          <button
            onClick={handleLogout}
            style={{
              width: "100%",
              padding: "11px 12px",
              borderRadius: 14,
              border: "1px solid var(--border)",
              background: "transparent",
              color: "var(--text)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <span style={{ width: 36, height: 36, borderRadius: 14, display: "grid", placeItems: "center", border: "1px solid var(--border)", background: "rgba(255,255,255,0.04)" }}>
              <LogOut size={18} />
            </span>
            Sair
          </button>
        </div>
      </aside>


      <main>
        <div className="container">{children}</div>
      </main>
    </div>

    
    
  );
}
