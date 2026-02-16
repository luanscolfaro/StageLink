import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import GlowCard from "../components/ui/GlowCard";
import Button from "../components/ui/Button";
import { UserPlus, UserMinus, Users, User, ArrowLeft } from "lucide-react";
import {
  getProfile,
  getFollowers,
  getFollowing,
  followUser,
  unfollowUser,
} from "../api/profile";

export default function ProfilePage() {
  const { username } = useParams();
  const navigate = useNavigate();

  const [profile, setProfile] = useState(null);
  const [tab, setTab] = useState("followers");
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function loadProfile() {
    setErr("");
    const res = await getProfile(username);
    setProfile(res.data);
  }

  async function loadTab(which) {
    setLoading(true);
    setErr("");
    try {
      if (which === "followers") {
        const res = await getFollowers(username);
        setFollowers(res.data);
      } else {
        const res = await getFollowing(username);
        setFollowing(res.data);
      }
    } finally {
      setLoading(false);
    }
  }

  async function boot() {
    try {
      await loadProfile();
      setTab("followers");
      await loadTab("followers");
    } catch (e) {
      console.log("Erro perfil:", e?.response?.status, e?.response?.data);
      const msg =
        e?.response?.data?.detail ||
        (e?.response?.status === 401 ? "Você precisa estar logado." : "") ||
        "Não consegui carregar esse perfil.";
      setErr(msg);
    }
  }

  async function handleToggleFollow() {
    if (!profile) return;
    setErr("");
    try {
      if (profile.is_following) {
        await unfollowUser(profile.id);
      } else {
        await followUser(profile.id);
      }
      await loadProfile();
      await loadTab(tab);
    } catch (e) {
      console.log("Erro seguir:", e?.response?.status, e?.response?.data);
      setErr("Não consegui atualizar o follow agora.");
    }
  }

  useEffect(() => {
    boot();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  if (err) {
    return (
      <div style={{ marginTop: 18 }}>
        <GlowCard style={{ marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <ArrowLeft size={16} />
            <Button type="button" variant="ghost" onClick={() => navigate(-1)}>
              Voltar
            </Button>
          </div>
        </GlowCard>

        <GlowCard>
          <div style={{ fontWeight: 900, marginBottom: 8 }}>Erro ao carregar perfil</div>
          <div style={{ color: "var(--muted)" }}>{err}</div>

          <div style={{ marginTop: 14, display: "flex", gap: 10, flexWrap: "wrap" }}>
            <Button type="button" onClick={boot}>Tentar novamente</Button>
            <Button type="button" variant="ghost" onClick={() => navigate("/feed")}>
              Ir para o Feed
            </Button>
          </div>
        </GlowCard>
      </div>
    );
  }

  if (!profile) {
    return <p style={{ color: "var(--muted)", marginTop: 18 }}>Carregando perfil...</p>;
  }

  const typeLabel = profile.account_type === "musician" ? "Músico" : "Contratante";

  return (
    <div style={{ marginTop: 18 }}>
      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <User size={18} />
              <div style={{ fontWeight: 950, letterSpacing: "-0.02em" }}>@{profile.username}</div>
            </div>
            <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 6 }}>{typeLabel}</div>

            <div style={{ display: "flex", gap: 12, marginTop: 10, color: "var(--muted)", fontSize: 13, flexWrap: "wrap" }}>
              <span><b style={{ color: "var(--text)" }}>{profile.followers_count}</b> seguidores</span>
              <span>•</span>
              <span><b style={{ color: "var(--text)" }}>{profile.following_count}</b> seguindo</span>
            </div>
          </div>

          <Button type="button" onClick={handleToggleFollow} variant={profile.is_following ? "ghost" : "primary"}>
            {profile.is_following ? <UserMinus size={16} /> : <UserPlus size={16} />}
            {profile.is_following ? "Deixar de seguir" : "Seguir"}
          </Button>
        </div>
      </GlowCard>

      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Button
            type="button"
            variant={tab === "followers" ? "primary" : "ghost"}
            onClick={() => { setTab("followers"); loadTab("followers"); }}
          >
            <Users size={16} /> Seguidores
          </Button>

          <Button
            type="button"
            variant={tab === "following" ? "primary" : "ghost"}
            onClick={() => { setTab("following"); loadTab("following"); }}
          >
            <Users size={16} /> Seguindo
          </Button>

          <Button type="button" variant="ghost" disabled>
            Avaliações (próximo passo)
          </Button>
        </div>
      </GlowCard>

      {loading && <p style={{ color: "var(--muted)" }}>Carregando...</p>}

      {tab === "followers" && (
        <div>
          {followers.length === 0 && <p style={{ color: "var(--muted)" }}>Ainda sem seguidores.</p>}
          {followers.map((u) => (
            <GlowCard key={u.id} style={{ marginBottom: 12, cursor: "pointer" }} onClick={() => navigate(`/profile/${u.username}`)}>
              <div style={{ fontWeight: 900 }}>@{u.username}</div>
              <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 4 }}>
                {u.account_type === "musician" ? "Músico" : "Contratante"}
              </div>
            </GlowCard>
          ))}
        </div>
      )}

      {tab === "following" && (
        <div>
          {following.length === 0 && <p style={{ color: "var(--muted)" }}>Ainda não segue ninguém.</p>}
          {following.map((u) => (
            <GlowCard key={u.id} style={{ marginBottom: 12, cursor: "pointer" }} onClick={() => navigate(`/profile/${u.username}`)}>
              <div style={{ fontWeight: 900 }}>@{u.username}</div>
              <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 4 }}>
                {u.account_type === "musician" ? "Músico" : "Contratante"}
              </div>
            </GlowCard>
          ))}
        </div>
      )}
    </div>
  );
}
