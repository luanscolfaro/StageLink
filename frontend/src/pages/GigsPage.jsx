import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import api from "../api/api";
import {
  listGigs,
  createGig,
  applyGig,
  getGigApplications,
  acceptApplication,
  rejectApplication,
} from "../api/gigs";

import GlowCard from "../components/ui/GlowCard";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Textarea from "../components/ui/Textarea";

import { Search, Send, CheckCircle2, XCircle, Plus, Briefcase } from "lucide-react";

export default function GigsPage() {
  const [me, setMe] = useState(null);

  const [gigs, setGigs] = useState([]);
  const [city, setCity] = useState("");
  const [tag, setTag] = useState("");
  const [loading, setLoading] = useState(false);

  const [newGig, setNewGig] = useState({
    title: "",
    description: "",
    city: "",
    date: "",
    fee: "",
    tags: "",
  });

  const [applyMsg, setApplyMsg] = useState({});
  const [openApps, setOpenApps] = useState(null);
  const [apps, setApps] = useState([]);

  async function loadMe() {
    const res = await api.get("/accounts/me/");
    setMe(res.data);
  }

  async function loadGigs() {
    setLoading(true);
    const res = await listGigs({ city: city || undefined, tag: tag || undefined });
    setGigs(res.data);
    setLoading(false);
  }

  useEffect(() => {
    loadMe();
    loadGigs();
  }, []);

  async function handleFilter(e) {
    e.preventDefault();
    loadGigs();
  }

  async function handleCreateGig(e) {
    e.preventDefault();
    try {
      const payload = {
        title: newGig.title,
        description: newGig.description,
        city: newGig.city,
        date: newGig.date || null,
        fee: newGig.fee ? Number(newGig.fee) : null,
        tags: newGig.tags,
      };
      await createGig(payload);
      setNewGig({ title: "", description: "", city: "", date: "", fee: "", tags: "" });
      await loadGigs();
      alert("Vaga publicada!");
    } catch {
      alert("Não consegui publicar. Verifique os campos e se você é contratante.");
    }
  }

  async function handleApply(gigId) {
    try {
      const msg = applyMsg[gigId] || "";
      await applyGig(gigId, msg);
      setApplyMsg((prev) => ({ ...prev, [gigId]: "" }));
      alert("Candidatura enviada!");
    } catch (err) {
      const detail =
        err?.response?.data?.detail ||
        err?.response?.data?.non_field_errors?.[0] ||
        "Não consegui candidatar.";
      console.log("Erro ao candidatar:", err?.response?.status, err?.response?.data);
      alert(detail);
    }
  }

  async function toggleApplications(gigId) {
    if (openApps === gigId) {
      setOpenApps(null);
      setApps([]);
      return;
    }

    try {
      const res = await getGigApplications(gigId);
      setApps(res.data);
      setOpenApps(gigId);
    } catch {
      alert("Você só pode ver candidaturas das vagas que você publicou.");
    }
  }

  async function handleAccept(appId) {
    await acceptApplication(appId);
    const res = await getGigApplications(openApps);
    setApps(res.data);
  }

  async function handleReject(appId) {
    await rejectApplication(appId);
    const res = await getGigApplications(openApps);
    setApps(res.data);
  }

  return (
    <Layout>
      <h1 className="h1">Buscar vagas</h1>
      <p className="p-muted">Encontre oportunidades e se candidate</p>
      <div className="hr" />

      {/* filtros */}
      <GlowCard>
        <form onSubmit={handleFilter} style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
          <div style={{ flex: 1, minWidth: 220 }}>
            <Input placeholder="Filtrar por cidade" value={city} onChange={(e) => setCity(e.target.value)} />
          </div>
          <div style={{ flex: 1, minWidth: 220 }}>
            <Input placeholder="Filtrar por tag (ex: forró)" value={tag} onChange={(e) => setTag(e.target.value)} />
          </div>
          <Button variant="ghost" type="submit">
            <Search size={16} /> Filtrar
          </Button>
        </form>
      </GlowCard>

      {/* criar vaga */}
      {me?.account_type === "contractor" && (
        <GlowCard style={{ marginTop: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <Briefcase size={18} />
            <div style={{ fontWeight: 900, letterSpacing: "-0.02em" }}>Publicar vaga</div>
          </div>

          <form onSubmit={handleCreateGig} style={{ display: "grid", gap: 10 }}>
            <Input
              placeholder="Título"
              value={newGig.title}
              onChange={(e) => setNewGig((p) => ({ ...p, title: e.target.value }))}
            />

            <Textarea
              placeholder="Descrição"
              value={newGig.description}
              onChange={(e) => setNewGig((p) => ({ ...p, description: e.target.value }))}
              rows={4}
            />

            <Input
              placeholder="Cidade"
              value={newGig.city}
              onChange={(e) => setNewGig((p) => ({ ...p, city: e.target.value }))}
            />

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              <div style={{ flex: 1, minWidth: 220 }}>
                <Input
                  type="date"
                  value={newGig.date}
                  onChange={(e) => setNewGig((p) => ({ ...p, date: e.target.value }))}
                />
              </div>
              <div style={{ flex: 1, minWidth: 220 }}>
                <Input
                  placeholder="Cachê (ex: 350)"
                  value={newGig.fee}
                  onChange={(e) => setNewGig((p) => ({ ...p, fee: e.target.value }))}
                />
              </div>
            </div>

            <Input
              placeholder="Tags (ex: forró, casamento, bar)"
              value={newGig.tags}
              onChange={(e) => setNewGig((p) => ({ ...p, tags: e.target.value }))}
            />

            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <Button type="submit">
                <Plus size={16} /> Publicar
              </Button>
            </div>
          </form>
        </GlowCard>
      )}

      {/* lista */}
      <div style={{ marginTop: 16 }}>
        {loading && <p style={{ color: "var(--muted)" }}>Carregando vagas...</p>}
        {!loading && gigs.length === 0 && <p style={{ color: "var(--muted)" }}>Nenhuma vaga encontrada.</p>}

        {gigs.map((g) => (
          <GlowCard key={g.id} style={{ marginTop: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start" }}>
              <div>
                <div style={{ fontWeight: 900, letterSpacing: "-0.02em", fontSize: 18 }}>{g.title}</div>
                <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 5 }}>
                  Publicado por <b>@{g.owner_username}</b>
                </div>
              </div>
              <div style={{ color: "var(--muted)", fontSize: 12 }}>
                {g.created_at ? new Date(g.created_at).toLocaleString() : ""}
              </div>
            </div>

            <div style={{ marginTop: 10, color: "var(--muted)", fontSize: 13 }}>
              <b style={{ color: "var(--text)" }}>Cidade:</b> {g.city}{" "}
              {g.date ? (
                <>
                  • <b style={{ color: "var(--text)" }}>Data:</b> {g.date}
                </>
              ) : null}
              {g.fee ? (
                <>
                  {" "}
                  • <b style={{ color: "var(--text)" }}>Cachê:</b> R$ {Number(g.fee).toFixed(2)}
                </>
              ) : null}
            </div>

            <div style={{ marginTop: 12, whiteSpace: "pre-wrap", lineHeight: 1.45 }}>
              {g.description}
            </div>

            {g.tags && (
              <div style={{ marginTop: 10, color: "var(--muted)", fontSize: 13 }}>
                <b style={{ color: "var(--text)" }}>Tags:</b> {g.tags}
              </div>
            )}

            <div style={{ display: "flex", gap: 10, marginTop: 14, flexWrap: "wrap", alignItems: "center" }}>
              {me?.account_type === "musician" && (
                <>
                  <div style={{ flex: 1, minWidth: 240 }}>
                    <Input
                      placeholder="Mensagem para o contratante (opcional)"
                      value={applyMsg[g.id] || ""}
                      onChange={(e) => setApplyMsg((p) => ({ ...p, [g.id]: e.target.value }))}
                    />
                  </div>
                  <Button type="button" onClick={() => handleApply(g.id)}>
                    <Send size={16} /> Candidatar
                  </Button>
                </>
              )}

              {me?.account_type === "contractor" && me?.id === g.owner && (
                <Button type="button" variant="ghost" onClick={() => toggleApplications(g.id)}>
                  {openApps === g.id ? "Fechar candidaturas" : "Ver candidaturas"}
                </Button>
              )}
            </div>

            {openApps === g.id && (
              <div style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid var(--border)" }}>
                <div style={{ fontWeight: 900, letterSpacing: "-0.02em" }}>Candidaturas</div>

                {apps.length === 0 && <p style={{ color: "var(--muted)", marginTop: 8 }}>Nenhuma ainda.</p>}

                {apps.map((a) => (
                  <div
                    key={a.id}
                    style={{
                      marginTop: 10,
                      padding: 12,
                      borderRadius: 16,
                      border: "1px solid var(--border)",
                      background: "rgba(255,255,255,0.03)",
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                      <div style={{ fontWeight: 800 }}>@{a.applicant_username}</div>
                      <div style={{ color: "var(--muted)", fontSize: 12 }}>{a.status}</div>
                    </div>

                    {a.message && <div style={{ marginTop: 8 }}>{a.message}</div>}

                    <div style={{ display: "flex", gap: 10, marginTop: 12, flexWrap: "wrap" }}>
                      <Button type="button" onClick={() => handleAccept(a.id)}>
                        <CheckCircle2 size={16} /> Aceitar
                      </Button>
                      <Button type="button" variant="danger" onClick={() => handleReject(a.id)}>
                        <XCircle size={16} /> Recusar
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </GlowCard>
        ))}
      </div>
    </Layout>
  );
}
