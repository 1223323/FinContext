"use client";

export default function GlobalError({ error, reset }) {
  return (
    <div style={{ padding: "40px", textAlign: "center", fontFamily: "sans-serif" }}>
      <h2 style={{ fontSize: "24px", color: "var(--color-accent-red)", marginBottom: "16px" }}>Something went wrong!</h2>
      <p style={{ color: "var(--color-text-secondary)", marginBottom: "24px" }}>{error?.message || "An unexpected error occurred."}</p>
      <button 
        onClick={() => reset()}
        style={{ padding: "10px 20px", background: "var(--color-accent-primary)", color: "white", border: "none", borderRadius: "8px", cursor: "pointer" }}
      >
        Try again
      </button>
    </div>
  );
}
