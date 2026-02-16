import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import { logout } from "../auth/auth";
import Feed from "../components/Feed";

export default function Home() {
  const [me, setMe] = useState(null);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function loadMe() {
    try {
      const res = await api.get("/accounts/me/");
      setMe(res.data);
    } catch (err) {
      setError("Não consegui carregar seu perfil. Faça login novamente.");
    }
  }

  useEffect(() => {
    loadMe();
  }, []);

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>StageLink</h1>
        <button onClick={handleLogout}>Sair</button>
      </div>

      {error && <p style={{ marginTop: 12, color: "tomato" }}>{error}</p>}

      {!me && !error && <p style={{ marginTop: 12 }}>Carregando...</p>}

      {me && (
        <div style={{ marginTop: 16, padding: 16, border: "1px solid #223", borderRadius: 12 }}>
          <p><b>Usuário:</b> {me.username}</p>
          <p><b>Tipo:</b> {me.account_type}</p>
          <p><b>Cidade:</b> {me.city || "-"} {me.state ? `- ${me.state}` : ""}</p>
        </div>
      )}

    <Feed />

    </div>
  );
}
