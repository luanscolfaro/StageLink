import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import GlowCard from "../components/ui/GlowCard";
import Button from "../components/ui/Button";
import Textarea from "../components/ui/Textarea";
import Avatar from "../components/ui/Avatar";
import Tags from "../components/ui/TagsInput";
import { UserPlus, UserMinus, Users, User, ArrowLeft, Star, MessageCircle, Heart } from "lucide-react";

import {
  getProfile,
  getFollowers,
  getFollowing,
  followUser,
  unfollowUser,
  getReviews,
  submitReview,
} from "../api/profile";

import api from "../api/api";
import { getUserPosts } from "../api/feed";

function resolveMedia(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  const apiBase = (import.meta?.env?.VITE_API_URL || "").trim();
  const base = apiBase ? apiBase.replace(/\/api\/?$/, "") : "http://127.0.0.1:8000";
  return `${base}${url}`;
}

function parseTags(str) {
  return (str || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function igUrl(handleOrUrl) {
  const raw = (handleOrUrl || "").trim();
  if (!raw) return "";
  const cleaned = raw
    .replace(/^https?:\/\/(www\.)?instagram\.com\//i, "")
    .replace(/^@/, "")
    .split(/[/?#]/)[0];
  if (!cleaned) return "";
  return `https://instagram.com/${cleaned}`;
}

function Stars({ value }) {
  const v = Math.round(value || 0);
  return (
    <span style={{ display: "inline-flex", gap: 4, verticalAlign: "middle" }}>
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          size={16}
          style={{
            color: i <= v ? "var(--brand)" : "var(--muted)",
            fill: i <= v ? "currentColor" : "transparent",
          }}
        />
      ))}
    </span>
  );
}

export default function ProfilePage() {
  const { username } = useParams();
  const navigate = useNavigate();

  const [me, setMe] = useState(null);

  const [profile, setProfile] = useState(null);
  const [tab, setTab] = useState("followers");
  const [followers, setFollowers] = useState([]);
  const [following, setFollowing] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  // reviews
  const [reviewsData, setReviewsData] = useState(null);
  const [myRating, setMyRating] = useState(5);
  const [myText, setMyText] = useState("");
  const [savingReview, setSavingReview] = useState(false);

  // posts
  const [posts, setPosts] = useState([]);
  const [loadingPosts, setLoadingPosts] = useState(false);

  async function loadMe() {
    const res = await api.get("/accounts/me/");
    setMe(res.data);
  }

  async function loadProfile() {
    setErr("");
    const res = await getProfile(username);
    setProfile(res.data);
  }

  async function loadUserPosts() {
    setLoadingPosts(true);
    try {
      const res = await getUserPosts(username);
      setPosts(res.data || []);
    } finally {
      setLoadingPosts(false);
    }
  }

  async function loadTab(which) {
    setLoading(true);
    setErr("");
    try {
      if (which === "followers") {
        const res = await getFollowers(username);
        setFollowers(res.data);
      } else if (which === "following") {
        const res = await getFollowing(username);
        setFollowing(res.data);
      } else if (which === "reviews") {
        const res = await getReviews(username);
        setReviewsData(res.data);

        const mine = res.data?.my_review;
        if (mine) {
          setMyRating(mine.rating || 5);
          setMyText(mine.text || "");
        } else {
          setMyRating(5);
          setMyText("");
        }
      }
    } finally {
      setLoading(false);
    }
  }

  async function boot() {
    try {
      await loadMe();
      await loadProfile();
      await loadUserPosts();
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

  function isMyProfile() {
    return !!me?.username && me.username === username;
  }

  async function handleSaveReview() {
    if (isMyProfile()) return;
    setSavingReview(true);
    setErr("");
    try {
      await submitReview(username, myRating, myText);
      await loadTab("reviews");
    } catch (e) {
      console.log("Erro review:", e?.response?.status, e?.response?.data);
      setErr(e?.response?.data?.detail || "Não consegui salvar a avaliação.");
    } finally {
      setSavingReview(false);
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

  if (!profile) return <p style={{ color: "var(--muted)", marginTop: 18 }}>Carregando perfil...</p>;

  const typeLabel = profile.account_type === "musician" ? "Músico" : "Contratante";

  // Perfil detalhado (se backend já estiver retornando)
  const mp = profile.musician_profile || null;
  const cp = profile.contractor_profile || null;

  const photo = resolveMedia(mp?.photo || cp?.photo || "");
  const bio = (mp?.bio || cp?.bio || "").trim();
  const city = (mp?.city || cp?.city || profile.city || "").trim();
  const state = (mp?.state || cp?.state || profile.state || "").trim();
  const whatsapp = (mp?.whatsapp || cp?.whatsapp || "").trim();
  const instagram = (mp?.instagram || cp?.instagram || "").trim();

  const instruments = parseTags(mp?.instruments || "");
  const genres = parseTags(mp?.genres || "");
  const company = (cp?.company_name || "").trim();

  return (
    <div style={{ marginTop: 18 }}>
      {/* Topo do perfil */}
      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
          <div style={{ display: "flex", gap: 14, alignItems: "center", flexWrap: "wrap" }}>
            <Avatar src={photo} username={profile.username} size={74} />

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
          </div>

          {/* Botão: editar só no próprio perfil */}
          {isMyProfile() ? (
            <Button type="button" onClick={() => navigate("/edit-profile")}>
              Editar perfil
            </Button>
          ) : (
            <Button type="button" onClick={handleToggleFollow} variant={profile.is_following ? "ghost" : "primary"}>
              {profile.is_following ? <UserMinus size={16} /> : <UserPlus size={16} />}
              {profile.is_following ? "Deixar de seguir" : "Seguir"}
            </Button>
          )}
        </div>

        {/* Detalhes do perfil */}
        {(bio || city || state || whatsapp || instagram || company || instruments.length || genres.length) && (
          <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--border)" }}>
            {bio && (
              <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.4 }}>
                {bio}
              </div>
            )}

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: bio ? 10 : 0, color: "var(--muted)", fontSize: 13 }}>
              {(city || state) && (
                <span>
                  {city}{city && state ? " - " : ""}{state}
                </span>
              )}
              {company && <span>• {company}</span>}
              {whatsapp && <span>• WhatsApp: {whatsapp}</span>}
              {instagram && (
                <span>
                  • Instagram:{" "}
                  <a
                    href={igUrl(instagram)}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: "var(--brand)" }}
                  >
                    @{igUrl(instagram).split("/").pop()}
                  </a>
                </span>
              )}
            </div>

            {instruments.length > 0 && (
              <>
                <div style={{ marginTop: 12, fontSize: 13, color: "var(--muted)" }}>Instrumentos</div>
                <Tags items={instruments} />
              </>
            )}

            {genres.length > 0 && (
              <>
                <div style={{ marginTop: 12, fontSize: 13, color: "var(--muted)" }}>Estilos</div>
                <Tags items={genres} />
              </>
            )}
          </div>
        )}
      </GlowCard>

      {/* Postagens do usuário (sempre visível) */}
      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ fontWeight: 950, letterSpacing: "-0.02em" }}>Postagens</div>
        <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 6 }}>
          Tudo que @{profile.username} publicou no StageLink.
        </div>
      </GlowCard>

      {loadingPosts && <p style={{ color: "var(--muted)" }}>Carregando postagens...</p>}

      {!loadingPosts && posts.length === 0 && (
        <p style={{ color: "var(--muted)" }}>Ainda não tem publicações.</p>
      )}

      {!loadingPosts && posts.map((post) => (
        <GlowCard key={post.id} style={{ marginBottom: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
            <div style={{ fontWeight: 900 }}>@{post.author_username}</div>
            <div style={{ color: "var(--muted)", fontSize: 12 }}>
              {new Date(post.created_at).toLocaleString()}
            </div>
          </div>

          <div style={{ marginTop: 10, whiteSpace: "pre-wrap", lineHeight: 1.4 }}>
            {post.content}
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 12, color: "var(--muted)", fontSize: 13, flexWrap: "wrap" }}>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
              <Heart size={16} /> {post.likes_count} curtidas
            </span>
            <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
              <MessageCircle size={16} /> {post.comments_count} comentários
            </span>
          </div>
        </GlowCard>
      ))}

      {/* Tabs antigas (seguidores/seguindo/avaliações) */}
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

          <Button
            type="button"
            variant={tab === "reviews" ? "primary" : "ghost"}
            onClick={() => { setTab("reviews"); loadTab("reviews"); }}
          >
            <Star size={16} /> Avaliações
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

      {tab === "reviews" && (
        <div>
          <GlowCard style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
              <div>
                <div style={{ fontWeight: 900 }}>Reputação</div>
                <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 6 }}>
                  <Stars value={reviewsData?.avg_rating || 0} />{" "}
                  <span style={{ marginLeft: 8 }}>
                    {reviewsData?.avg_rating || 0} ({reviewsData?.count || 0})
                  </span>
                </div>
              </div>
            </div>
          </GlowCard>

          {!isMyProfile() && (
            <GlowCard style={{ marginBottom: 12 }}>
              <div style={{ fontWeight: 900, marginBottom: 8 }}>Deixe sua avaliação</div>

              <div style={{ display: "grid", gap: 10 }}>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
                  <div style={{ color: "var(--muted)", fontSize: 13 }}>Nota</div>
                  <select
                    value={myRating}
                    onChange={(e) => setMyRating(Number(e.target.value))}
                    style={{
                      padding: "10px 12px",
                      borderRadius: 14,
                      border: "1px solid var(--border)",
                      background: "rgba(255,255,255,0.03)",
                      color: "var(--text)",
                      outline: "none",
                    }}
                  >
                    {[5, 4, 3, 2, 1].map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>

                  <span style={{ marginLeft: 6 }}><Stars value={myRating} /></span>
                </div>

                <Textarea
                  placeholder="Comentário (opcional). Ex: pontual, profissional, comunicação..."
                  rows={3}
                  value={myText}
                  onChange={(e) => setMyText(e.target.value)}
                />

                <div style={{ display: "flex", justifyContent: "flex-end" }}>
                  <Button type="button" onClick={handleSaveReview} disabled={savingReview}>
                    {savingReview ? "Salvando..." : "Salvar avaliação"}
                  </Button>
                </div>
              </div>
            </GlowCard>
          )}

          <div>
            {(reviewsData?.items || []).length === 0 && (
              <p style={{ color: "var(--muted)" }}>Sem avaliações ainda.</p>
            )}

            {(reviewsData?.items || []).map((r) => (
              <GlowCard key={r.id} style={{ marginBottom: 12 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
                  <div style={{ fontWeight: 900, cursor: "pointer" }} onClick={() => navigate(`/profile/${r.reviewer_username}`)}>
                    @{r.reviewer_username}
                  </div>
                  <Stars value={r.rating} />
                </div>

                {r.text && (
                  <div style={{ marginTop: 10, whiteSpace: "pre-wrap", lineHeight: 1.4 }}>
                    {r.text}
                  </div>
                )}

                <div style={{ marginTop: 10, color: "var(--muted)", fontSize: 12 }}>
                  {new Date(r.created_at).toLocaleString()}
                </div>
              </GlowCard>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
