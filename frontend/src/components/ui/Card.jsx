export default function Card({ children, style }) {
    return (
      <div
        style={{
          background: "var(--panel)",
          border: "1px solid var(--border)",
          borderRadius: 18,
          padding: 16,
          boxShadow: "var(--shadow)",
          ...style,
        }}
      >
        {children}
      </div>
    );
  }
  