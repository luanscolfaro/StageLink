export default function Avatar({ src, username = "?", size = 54 }) {
    const initials = (username || "?").slice(0, 2).toUpperCase();
  
    return (
      <div
        style={{
          width: size,
          height: size,
          borderRadius: Math.round(size / 3),
          border: "1px solid var(--border)",
          overflow: "hidden",
          background: "rgba(255,255,255,0.04)",
          display: "grid",
          placeItems: "center",
          color: "var(--muted)",
          fontWeight: 900,
          letterSpacing: "-0.02em",
        }}
      >
        {src ? (
          <img
            src={src}
            alt="avatar"
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        ) : (
          initials
        )}
      </div>
    );
  }
  