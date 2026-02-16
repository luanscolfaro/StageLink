import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";

export default function MeRedirect() {
  const navigate = useNavigate();
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get("/accounts/me/");
        const username = res.data?.username;

        if (!username) {
          setErr("Não consegui identificar seu usuário.");
          return;
        }

        navigate(`/profile/${username}`, { replace: true });
      } catch (e) {
        console.log("Erro /accounts/me:", e?.response?.status, e?.response?.data);
        setErr("Você precisa estar logado.");
      }
    })();
  }, [navigate]);

  if (err) return <p style={{ color: "var(--muted)", marginTop: 18 }}>{err}</p>;
  return <p style={{ color: "var(--muted)", marginTop: 18 }}>Abrindo seu perfil...</p>;
}
