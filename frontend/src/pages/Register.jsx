import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/api";
import Card from "../components/ui/Card";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { UserPlus, Music2, Briefcase, ArrowLeft } from "lucide-react";

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    account_type: "musician",
    phone: "",
    city: "",
    state: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function setField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("/accounts/register/", form);
      navigate("/");
    } catch (err) {
      const msg =
        err?.response?.data?.username?.[0] ||
        err?.response?.data?.email?.[0] ||
        err?.response?.data?.password?.[0] ||
        err?.response?.data?.detail ||
        "Não consegui criar sua conta. Verifique os campos.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const typeBtn = (active) => ({
    flex: 1,
    padding: "10px 12px",
    borderRadius: 14,
    border: `1px solid ${active ? "rgba(56,189,248,0.35)" : "var(--border)"}`,
    background: active ? "rgba(56,189,248,0.14)" : "rgba(255,255,255,0.03)",
    color: "var(--text)",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: 10,
    fontWeight: 700,
  });

  return (
    <div className="container" style={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <div style={{ width: "100%", maxWidth: 560 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
          <div style={{ marginBottom: 14 }}>
            <h1 className="h1">Criar conta</h1>
            <p className="p-muted">Entre no StageLink e conecte sua música a oportunidades</p>
          </div>

          <Button variant="ghost" type="button" onClick={() => navigate("/")}>
            <ArrowLeft size={16} /> Voltar
          </Button>
        </div>

        <Card>
          <form onSubmit={handleSubmit} style={{ display: "grid", gap: 12 }}>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button
                type="button"
                style={typeBtn(form.account_type === "musician")}
                onClick={() => setField("account_type", "musician")}
              >
                <Music2 size={16} /> Músico
              </button>

              <button
                type="button"
                style={typeBtn(form.account_type === "contractor")}
                onClick={() => setField("account_type", "contractor")}
              >
                <Briefcase size={16} /> Contratante
              </button>
            </div>

            <Input
              placeholder="Usuário (obrigatório)"
              value={form.username}
              onChange={(e) => setField("username", e.target.value)}
              required
            />

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <Input
                placeholder="Nome"
                value={form.first_name}
                onChange={(e) => setField("first_name", e.target.value)}
              />
              <Input
                placeholder="Sobrenome"
                value={form.last_name}
                onChange={(e) => setField("last_name", e.target.value)}
              />
            </div>

            <Input
              placeholder="Email"
              type="email"
              value={form.email}
              onChange={(e) => setField("email", e.target.value)}
            />

            <Input
              placeholder="Senha (obrigatório)"
              type="password"
              value={form.password}
              onChange={(e) => setField("password", e.target.value)}
              required
            />

            <div style={{ display: "grid", gridTemplateColumns: "1fr 120px", gap: 10 }}>
              <Input
                placeholder="Cidade"
                value={form.city}
                onChange={(e) => setField("city", e.target.value)}
              />
              <Input
                placeholder="UF"
                value={form.state}
                onChange={(e) => setField("state", e.target.value.toUpperCase())}
                maxLength={2}
              />
            </div>

            <Input
              placeholder="Telefone"
              value={form.phone}
              onChange={(e) => setField("phone", e.target.value)}
            />

            <Button type="submit" disabled={loading}>
              <UserPlus size={16} />
              {loading ? "Criando..." : "Criar conta"}
            </Button>

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

        <p className="p-muted" style={{ marginTop: 10 }}>
          Ao criar a conta, você já pode entrar e usar o feed e buscar vagas.
        </p>
      </div>
    </div>
  );
}
