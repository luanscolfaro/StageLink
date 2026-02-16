import { useEffect, useState } from "react";
import GlowCard from "../components/ui/GlowCard";
import Input from "../components/ui/Input";
import Button from "../components/ui/Button";
import { Search, UserPlus, UserMinus, Users } from "lucide-react";
import { searchUsers, followUser, unfollowUser, getProfile } from "../api/profile";
import { useNavigate } from "react-router-dom";

export default function SearchPeople() {
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function load() {
    setLoading(true);
    try {
      const res = await searchUsers(q);
      const list = res.data;

      // opcional: marcar follow/unfollow com uma chamada extra por usuário (leve e simples)
      // para portfólio, vamos sem isso por enquanto
      setItems(list);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleFollow(userId) {
    await followUser(userId);
    await load();
  }

  async function handleUnfollow(userId) {
    await unfollowUser(userId);
    await load();
  }

  return (
    <div style={{ marginTop: 18 }}>
      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <Users size={18} />
          <div style={{ fontWeight: 900, letterSpacing: "-0.02em" }}>Buscar pessoas</div>
        </div>

        <div style={{ marginTop: 12, display: "flex", gap: 10, flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: 240 }}>
            <Input
              placeholder="Digite um @username..."
              value={q}
              onChange={(e) => setQ(e.target.value)}
            />
          </div>
          <Button type="button" onClick={load} disabled={loading}>
            <Search size={16} />
            {loading ? "Buscando..." : "Buscar"}
          </Button>
        </div>

        <div style={{ marginTop: 10, color: "var(--muted)", fontSize: 13 }}>
          Dica: procure pelo nome de usuário (ex: luan, banda, cantor)
        </div>
      </GlowCard>

      {items.length === 0 && (
        <p style={{ color: "var(--muted)" }}>Nenhum perfil encontrado.</p>
      )}

      {items.map((u) => (
        <GlowCard key={u.id} style={{ marginBottom: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
            <div style={{ cursor: "pointer" }} onClick={() => navigate(`/profile/${u.username}`)}>
              <div style={{ fontWeight: 900 }}>@{u.username}</div>
              <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 4 }}>
                {u.account_type === "musician" ? "Músico" : "Contratante"}
              </div>
            </div>

            {/* Por enquanto, botões simples. A indicação de "seguindo" vai estar no perfil */}
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <Button type="button" variant="ghost" onClick={() => handleFollow(u.id)}>
                <UserPlus size={16} /> Seguir
              </Button>
              <Button type="button" variant="ghost" onClick={() => handleUnfollow(u.id)}>
                <UserMinus size={16} /> Deixar
              </Button>
            </div>
          </div>
        </GlowCard>
      ))}
    </div>
  );
}
