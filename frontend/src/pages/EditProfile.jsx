import { useEffect, useMemo, useState } from "react";
import GlowCard from "../components/ui/GlowCard";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Textarea from "../components/ui/Textarea";
import Avatar from "../components/ui/Avatar";
import TagsInput from "../components/ui/TagsInput";
import CropPhotoModal from "../components/CropPhotoModal";
import { Camera, Save, User } from "lucide-react";
import { getMyProfile, updateMyProfile } from "../api/myProfile";
import { formatE164Like } from "../utils/phone";

function resolveMedia(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  const apiBase = (import.meta?.env?.VITE_API_URL || "").trim();
  const base = apiBase ? apiBase.replace(/\/api\/?$/, "") : "http://127.0.0.1:8000";
  return `${base}${url}`;
}

function toTags(str) {
  return (str || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
}

function toCSV(tags) {
  return (tags || []).join(", ");
}

export default function EditProfile() {
  const [accountType, setAccountType] = useState("");
  const [data, setData] = useState({});
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");

  // foto + crop
  const [rawPreview, setRawPreview] = useState(null);
  const [cropOpen, setCropOpen] = useState(false);
  const [photoBlob, setPhotoBlob] = useState(null);

  // tags
  const instrumentsTags = useMemo(() => toTags(data.instruments), [data.instruments]);
  const genresTags = useMemo(() => toTags(data.genres), [data.genres]);

  function setField(key, value) {
    setData((prev) => ({ ...prev, [key]: value }));
  }

  async function load() {
    setMsg("");
    const res = await getMyProfile();
    setAccountType(res.data.account_type);
    setData(res.data.profile || {});
  }

  async function save() {
    setSaving(true);
    setMsg("");
    try {
      const fd = new FormData();

      // normalizações
      const payload = { ...data };
      payload.whatsapp = formatE164Like(payload.whatsapp || "");
      payload.instagram = (payload.instagram || "").trim().replace(/^https?:\/\/(www\.)?instagram\.com\//i, "").replace(/^@/, "");
      payload.instruments = payload.instruments || "";
      payload.genres = payload.genres || "";

      Object.entries(payload).forEach(([k, v]) => fd.append(k, v ?? ""));

      if (photoBlob) {
        fd.append("photo", photoBlob, "profile.jpg");
      }

      await updateMyProfile(fd);
      setMsg("Perfil atualizado!");
      setPhotoBlob(null);
      setRawPreview(null);
      await load();
    } catch (e) {
      console.log("Erro salvar perfil:", e?.response?.status, e?.response?.data);
      setMsg(e?.response?.data?.detail || "Não consegui salvar seu perfil.");
    } finally {
      setSaving(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const isMusician = accountType === "musician";
  const photoUrl = resolveMedia(data.photo);

  return (
    <div style={{ marginTop: 18 }}>
      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <User size={18} />
          <div style={{ fontWeight: 950, letterSpacing: "-0.02em" }}>Editar perfil</div>
        </div>
        <div style={{ color: "var(--muted)", fontSize: 13, marginTop: 8 }}>
          Preencha com calma. Isso vai aparecer no seu perfil público.
        </div>
      </GlowCard>

      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "flex", gap: 14, alignItems: "center", flexWrap: "wrap" }}>
          <Avatar src={rawPreview || photoUrl} username="SL" size={84} />

          <div style={{ display: "grid", gap: 8 }}>
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
                width: "fit-content",
              }}
            >
              <Camera size={16} />
              Escolher foto
              <input
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (!f) return;
                  const url = URL.createObjectURL(f);
                  setRawPreview(url);
                  setCropOpen(true);
                }}
              />
            </label>

            <div style={{ color: "var(--muted)", fontSize: 12 }}>
              Você vai poder recortar antes de salvar.
            </div>
          </div>
        </div>
      </GlowCard>

      <GlowCard style={{ marginBottom: 16 }}>
        <div style={{ display: "grid", gap: 12 }}>
          <div style={{ fontSize: 13, color: "var(--muted)" }}>Bio</div>
          <Textarea
            placeholder="Ex: Toco em eventos, barzinho, casamentos. Repertório variado e pontualidade."
            rows={4}
            value={data.bio || ""}
            onChange={(e) => setField("bio", e.target.value)}
          />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 120px", gap: 12 }}>
            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>Cidade</div>
              <Input
                placeholder="Digite sua cidade"
                value={data.city || ""}
                onChange={(e) => setField("city", e.target.value)}
              />
            </div>

            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>UF</div>
              <Input
                placeholder="PB"
                value={data.state || ""}
                onChange={(e) => setField("state", e.target.value.toUpperCase().slice(0, 2))}
              />
            </div>
          </div>

          {isMusician ? (
            <>
              <TagsInput
                label="Instrumentos"
                value={instrumentsTags}
                onChange={(tags) => setField("instruments", toCSV(tags))}
                placeholder="Ex: violão, voz, guitarra"
              />

              <TagsInput
                label="Estilos"
                value={genresTags}
                onChange={(tags) => setField("genres", toCSV(tags))}
                placeholder="Ex: forró, pop, worship"
              />
            </>
          ) : (
            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>Empresa / Local</div>
              <Input
                placeholder="Ex: Bar do Centro, Produtora XPTO"
                value={data.company_name || ""}
                onChange={(e) => setField("company_name", e.target.value)}
              />
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>WhatsApp</div>
              <Input
                placeholder="Ex: +5583999999999"
                value={data.whatsapp || ""}
                onChange={(e) => setField("whatsapp", formatE164Like(e.target.value))}
              />
              <div style={{ fontSize: 12, color: "var(--muted)" }}>
                Formato internacional. Ex: +55 + DDD + número
              </div>
            </div>

            <div style={{ display: "grid", gap: 8 }}>
              <div style={{ fontSize: 13, color: "var(--muted)" }}>Instagram</div>
              <Input
                placeholder="Ex: luan.scolfaro (sem @)"
                value={data.instagram || ""}
                onChange={(e) => setField("instagram", e.target.value)}
              />
              <div style={{ fontSize: 12, color: "var(--muted)" }}>
                Pode colar link ou @, o sistema ajusta.
              </div>
            </div>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: 10, flexWrap: "wrap" }}>
            <Button type="button" onClick={save} disabled={saving}>
              <Save size={16} />
              {saving ? "Salvando..." : "Salvar"}
            </Button>
          </div>

          {msg && <div style={{ color: "var(--muted)", fontSize: 13 }}>{msg}</div>}
        </div>
      </GlowCard>

      <CropPhotoModal
        open={cropOpen}
        imageSrc={rawPreview}
        onClose={() => setCropOpen(false)}
        onDone={(blob) => {
          setPhotoBlob(blob);
          setCropOpen(false);
        }}
      />
    </div>
  );
}
