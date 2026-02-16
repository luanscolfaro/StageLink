import { useRef } from "react";

export default function GlowCard({ children, style }) {
  const ref = useRef(null);

  function onMove(e) {
    const el = ref.current;
    if (!el) return;
    const r = el.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    el.style.setProperty("--mx", `${x}px`);
    el.style.setProperty("--my", `${y}px`);
  }

  return (
    <div
      ref={ref}
      onMouseMove={onMove}
      className="glow-card"
      style={{
        position: "relative",
        borderRadius: 18,
        border: "1px solid var(--border)",
        background: "var(--panel)",
        padding: 16,
        boxShadow: "var(--shadow)",
        overflow: "hidden",
        transition: "transform .18s ease, border .18s ease",
        ...style,
      }}
    >
      <div className="glow-layer" />
      <div style={{ position: "relative", zIndex: 1 }}>{children}</div>
    </div>
  );
}
