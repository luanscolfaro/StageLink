export default function Button({ children, variant="primary", ...props }) {
    const base = {
      padding: "10px 14px",
      borderRadius: 14,
      border: "1px solid var(--border)",
      cursor: "pointer",
      display: "inline-flex",
      alignItems: "center",
      gap: 10,
      transition: "transform .06s ease, background .2s ease, border .2s ease",
      userSelect: "none",
    };
  
    const variants = {
      primary: {
        background: "linear-gradient(135deg, var(--brand), var(--brand2))",
        color: "#06101b",
        border: "1px solid rgba(56,189,248,0.45)",
        boxShadow: "0 16px 35px rgba(56,189,248,0.10)",
        fontWeight: 700,
      },
      ghost: {
        background: "transparent",
        color: "var(--text)",
      },
      danger: {
        background: "rgba(251,113,133,0.12)",
        color: "var(--text)",
        border: "1px solid rgba(251,113,133,0.35)",
      },
    };
  
    return (
      <button
        {...props}
        style={{ ...base, ...variants[variant], opacity: props.disabled ? 0.6 : 1 }}
        onMouseDown={(e) => e.currentTarget.style.transform = "translateY(1px)"}
        onMouseUp={(e) => e.currentTarget.style.transform = "translateY(0px)"}
        onMouseLeave={(e) => e.currentTarget.style.transform = "translateY(0px)"}
      >
        {children}
      </button>
    );
  }
  