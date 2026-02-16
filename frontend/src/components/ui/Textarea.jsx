export default function Textarea(props) {
    return (
      <textarea
        {...props}
        style={{
          width: "100%",
          padding: 12,
          borderRadius: 14,
          border: "1px solid var(--border)",
          background: "rgba(255,255,255,0.04)",
          color: "var(--text)",
          outline: "none",
          resize: "vertical",
        }}
      />
    );
  }
  