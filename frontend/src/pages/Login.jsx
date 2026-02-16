import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { Music2, LockKeyhole } from "lucide-react";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      const res = await api.post("/auth/login/", { username, password });
      localStorage.setItem("access", res.data.access);
      localStorage.setItem("refresh", res.data.refresh);
      navigate("/feed");
    } catch {
      setError("Usuário ou senha inválidos");
    }
  }

  return (
    <div
      className="container"
      style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}
    >
      <div style={{ width: "100%", maxWidth: 420 }}>
        <div style={{ marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div
              style={{
                width: 42,
                height: 42,
                borderRadius: 16,
                background:
                  "linear-gradient(135deg, var(--brand), var(--brand2))",
                display: "grid",
                placeItems: "center",
                color: "#06101b",
                fontWeight: 900,
              }}
            >
              SL
            </div>
            <div>
              <h1 className="h1">StageLink</h1>
              <p className="p-muted">
                Entre para conectar músicos e contratantes
              </p>
            </div>
          </div>
        </div>

        <Card>
          <form
            onSubmit={handleSubmit}
            style={{ display: "grid", gap: 12 }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                color: "var(--muted)",
                fontSize: 13,
              }}
            >
              <Music2 size={16} />
              Login
            </div>

            <Input
              placeholder="Usuário"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            <div style={{ position: "relative" }}>
              <Input
                type="password"
                placeholder="Senha"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <span
                style={{
                  position: "absolute",
                  right: 12,
                  top: 12,
                  color: "var(--muted)",
                }}
              >
                <LockKeyhole size={16} />
              </span>
            </div>

            <Button type="submit">Entrar</Button>

            <div style={{ color: "var(--muted)", fontSize: 13 }}>
            Não tem conta? <a href="/register" style={{ color: "var(--brand)" }}>Criar conta</a>
            </div>


            {error && (
              <div
                style={{
                  color: "var(--danger)",
                  background: "rgba(251,113,133,0.10)",
                  border: "1px solid rgba(251,113,133,0.25)",
                  padding: 10,
                  borderRadius: 14,
                }}
              >
                {error}
              </div>
            )}
          </form>
        </Card>
      </div>
    </div>
  );
}
