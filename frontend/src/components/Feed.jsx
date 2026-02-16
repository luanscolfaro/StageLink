import { useEffect, useMemo, useState } from "react";
import {
  getFeed,
  createPost,
  likePost,
  unlikePost,
  getComments,
  addComment,
} from "../api/feed";

import GlowCard from "./ui/GlowCard";
import Button from "./ui/Button";
import Input from "./ui/Input";
import Textarea from "./ui/Textarea";

import {
  Heart,
  MessageCircle,
  SendHorizonal,
  Image as ImageIcon,
  Loader2,
} from "lucide-react";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [content, setContent] = useState("");
  const [loadingPost, setLoadingPost] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const [openComments, setOpenComments] = useState({});
  const [commentsByPost, setCommentsByPost] = useState({});
  const [commentText, setCommentText] = useState({});

  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);

  const canPublish = useMemo(() => !!content.trim() || !!image, [content, image]);

  async function loadFeed() {
    const res = await getFeed();
    setPosts(res.data);
  }

  async function handlePost(e) {
    e.preventDefault();
    if (!canPublish || loadingPost) return;

    setErrorMsg("");
    setLoadingPost(true);

    try {
      await createPost(content, image);

      setContent("");
      setImage(null);
      setPreview(null);

      await loadFeed();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.log("Erro ao publicar:", err?.response?.status, err?.response?.data);
      const msg =
        err?.response?.data?.detail ||
        err?.response?.data?.content?.[0] ||
        "Não consegui publicar. Tente novamente.";
      setErrorMsg(msg);
    } finally {
      setLoadingPost(false);
    }
  }

  // garante URL completa para /media/...
  function resolveImageUrl(url) {
    if (!url) return null;
    if (url.startsWith("http")) return url;

    const apiBase = (import.meta?.env?.VITE_API_URL || "").trim();
    const base = apiBase ? apiBase.replace(/\/api\/?$/, "") : "http://127.0.0.1:8000";
    return `${base}${url}`;
  }

  async function handleToggleLike(post) {
    try {
      if (post.liked_by_me) {
        await unlikePost(post.id);
      } else {
        await likePost(post.id);
      }
      await loadFeed();
    } catch (err) {
      console.log("Erro ao curtir/descurtir:", err?.response?.status, err?.response?.data);
    }
  }

  async function toggleComments(postId) {
    const isOpen = !!openComments[postId];
    setOpenComments((prev) => ({ ...prev, [postId]: !isOpen }));

    if (!isOpen) {
      const res = await getComments(postId);
      setCommentsByPost((prev) => ({ ...prev, [postId]: res.data }));
    }
  }

  async function handleAddComment(postId) {
    const text = (commentText[postId] || "").trim();
    if (!text) return;

    try {
      await addComment(postId, text);
      setCommentText((prev) => ({ ...prev, [postId]: "" }));

      const res = await getComments(postId);
      setCommentsByPost((prev) => ({ ...prev, [postId]: res.data }));
      await loadFeed();
    } catch (err) {
      console.log("Erro ao comentar:", err?.response?.status, err?.response?.data);
    }
  }

  useEffect(() => {
    loadFeed();
  }, []);

  return (
    <div style={{ marginTop: 18 }}>
      {/* Criar post */}
      <GlowCard style={{ marginBottom: 18 }}>
        <form onSubmit={handlePost} style={{ display: "grid", gap: 12 }}>
          <div>
            <div style={{ fontWeight: 900, letterSpacing: "-0.02em" }}>
              Nova publicação
            </div>
            <div style={{ fontSize: 13, color: "var(--muted)", marginTop: 4 }}>
              Compartilhe algo sobre sua música, agenda ou trabalho
            </div>
          </div>

          <Textarea
            placeholder="Escreva aqui..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
          />

          <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
            <label
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 10,
                padding: "10px 14px",
                borderRadius: 14,
                border: "1px solid var(--border)",
                background: "rgba(255,255,255,0.03)",
                cursor: "pointer",
                color: "var(--text)",
              }}
            >
              <ImageIcon size={16} />
              {image ? "Trocar imagem" : "Adicionar imagem"}
              <input
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  setImage(file);
                  setPreview(URL.createObjectURL(file));
                }}
              />
            </label>

            {image && (
              <Button
                type="button"
                variant="danger"
                onClick={() => {
                  setImage(null);
                  setPreview(null);
                }}
              >
                Remover
              </Button>
            )}
          </div>

          {preview && (
            <img
              src={preview}
              alt="preview"
              style={{
                width: "100%",
                maxHeight: 320,
                borderRadius: 16,
                objectFit: "cover",
                border: "1px solid var(--border)",
              }}
            />
          )}

          {errorMsg && (
            <div
              style={{
                color: "var(--danger)",
                background: "rgba(251,113,133,0.10)",
                border: "1px solid rgba(251,113,133,0.25)",
                padding: 10,
                borderRadius: 14,
              }}
            >
              {errorMsg}
            </div>
          )}

          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Button type="submit" disabled={!canPublish || loadingPost}>
              {loadingPost ? <Loader2 size={16} className="spin" /> : <SendHorizonal size={16} />}
              {loadingPost ? "Publicando..." : "Publicar"}
            </Button>
          </div>
        </form>
      </GlowCard>

      {/* Posts */}
      {posts.length === 0 && <p style={{ color: "var(--muted)" }}>Nenhuma publicação ainda.</p>}

      {posts.map((post) => {
        const liked = !!post.liked_by_me;

        return (
          <GlowCard key={post.id} style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
              <div>
                <div style={{ fontWeight: 900 }}>@{post.author_username}</div>
                <div style={{ color: "var(--muted)", fontSize: 12, marginTop: 3 }}>
                  {new Date(post.created_at).toLocaleString()}
                </div>
              </div>

              <div style={{ display: "flex", gap: 10, alignItems: "center", color: "var(--muted)", fontSize: 12 }}>
                <span>{post.likes_count} curtidas</span>
                <span>•</span>
                <span>{post.comments_count} comentários</span>
              </div>
            </div>

            {post.image && (
              <img
                src={resolveImageUrl(post.image)}
                alt="post"
                style={{
                  width: "100%",
                  marginTop: 12,
                  borderRadius: 16,
                  objectFit: "cover",
                  border: "1px solid var(--border)",
                  maxHeight: 520,
                }}
              />
            )}

            <div style={{ marginTop: 12, whiteSpace: "pre-wrap", lineHeight: 1.4 }}>
              {post.content}
            </div>

            <div style={{ display: "flex", gap: 10, marginTop: 14, flexWrap: "wrap" }}>
              <Button
                variant="ghost"
                type="button"
                onClick={() => handleToggleLike(post)}
                style={{
                  borderColor: liked ? "rgba(56,189,248,0.35)" : undefined,
                  background: liked ? "rgba(56,189,248,0.12)" : undefined,
                }}
              >
                <Heart
                  size={16}
                  style={{
                    color: liked ? "var(--brand)" : "var(--text)",
                    fill: liked ? "currentColor" : "transparent",
                  }}
                />
                {liked ? "Curtido" : "Curtir"}
              </Button>

              <Button variant="ghost" type="button" onClick={() => toggleComments(post.id)}>
                <MessageCircle size={16} /> Comentários
              </Button>
            </div>

            {openComments[post.id] && (
              <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--border)" }}>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <div style={{ flex: 1, minWidth: 220 }}>
                    <Input
                      placeholder="Escreva um comentário..."
                      value={commentText[post.id] || ""}
                      onChange={(e) =>
                        setCommentText((prev) => ({ ...prev, [post.id]: e.target.value }))
                      }
                    />
                  </div>
                  <Button type="button" onClick={() => handleAddComment(post.id)}>
                    Enviar
                  </Button>
                </div>

                <div style={{ marginTop: 12 }}>
                  {(commentsByPost[post.id] || []).length === 0 && (
                    <p style={{ color: "var(--muted)" }}>Sem comentários ainda.</p>
                  )}

                  {(commentsByPost[post.id] || []).map((c) => (
                    <div
                      key={c.id}
                      style={{
                        marginTop: 10,
                        padding: 12,
                        borderRadius: 16,
                        border: "1px solid var(--border)",
                        background: "rgba(255,255,255,0.03)",
                      }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", gap: 12 }}>
                        <div style={{ fontWeight: 800 }}>@{c.user_username}</div>
                        <div style={{ color: "var(--muted)", fontSize: 12 }}>
                          {new Date(c.created_at).toLocaleString()}
                        </div>
                      </div>
                      <div style={{ marginTop: 8 }}>{c.text}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </GlowCard>
        );
      })}

      <style>{`
        .spin { animation: spin 1s linear infinite; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
