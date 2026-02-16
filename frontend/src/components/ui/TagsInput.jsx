import { useMemo, useState } from "react";

export default function TagsInput({ label, value = [], onChange, placeholder }) {
  const [text, setText] = useState("");

  const tags = useMemo(() => (Array.isArray(value) ? value : []), [value]);

  function addTag(raw) {
    const t = (raw || "").trim();
    if (!t) return;
    if (tags.some((x) => x.toLowerCase() === t.toLowerCase())) return;
    onChange([...tags, t]);
  }

  function removeTag(t) {
    onChange(tags.filter((x) => x !== t));
  }

  return (
    <div style={{ display: "grid", gap: 8 }}>
      {label && <div style={{ fontSize: 13, color: "var(--muted)" }}>{label}</div>}

      <div
        style={{
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
          padding: 10,
          borderRadius: 16,
          border: "1px solid var(--border)",
          background: "rgba(255,255,255,0.03)",
        }}
      >
        {tags.map((t) => (
          <span
            key={t}
            style={{
              display: "inline-flex",
              gap: 8,
              alignItems: "center",
              padding: "6px 10px",
              borderRadius: 999,
              border: "1px solid rgba(255,255,255,0.10)",
              background: "rgba(255,255,255,0.04)",
              fontSize: 13,
            }}
          >
            {t}
            <button
              type="button"
              onClick={() => removeTag(t)}
              style={{
                border: "none",
                background: "transparent",
                color: "var(--muted)",
                cursor: "pointer",
                fontWeight: 900,
              }}
              aria-label="remover"
            >
              ×
            </button>
          </span>
        ))}

        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === ",") {
              e.preventDefault();
              addTag(text.replace(",", ""));
              setText("");
            }
            if (e.key === "Backspace" && !text && tags.length) {
              removeTag(tags[tags.length - 1]);
            }
          }}
          placeholder={placeholder || "Digite e pressione Enter"}
          style={{
            flex: 1,
            minWidth: 160,
            border: "none",
            outline: "none",
            background: "transparent",
            color: "var(--text)",
            padding: "6px 8px",
          }}
        />
      </div>

      <div style={{ fontSize: 12, color: "var(--muted)" }}>
        Dica: pressione Enter para criar uma tag.
      </div>
    </div>
  );
}
