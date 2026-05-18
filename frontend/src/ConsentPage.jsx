import { useState } from "react";

export default function ConsentPage({ onConsent }) {
  const [loading, setLoading] = useState(false);

  const handleYes = () => {
    setLoading(true);

    // Save consent (important for research compliance)
    localStorage.setItem("user_consent", "true");

    onConsent(true);
  };

  const handleNo = () => {
    localStorage.setItem("user_consent", "false");
    onConsent(false);
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Participant Consent</h2>

        <p style={styles.text}>
          Before you begin, please confirm your consent to participate in this
          research program.
        </p>

        <ul style={styles.list}>
          <li>Your participation is voluntary</li>
          <li>Your data will be securely stored and anonymised</li>
          <li>You may withdraw at any time</li>
        </ul>

        <div style={styles.buttonRow}>
          <button style={styles.noButton} onClick={handleNo}>
            No, I do not consent
          </button>

          <button style={styles.yesButton} onClick={handleYes}>
            Yes, I consent
          </button>
        </div>

        {loading && <p>Redirecting...</p>}
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f5f9fc",
    padding: "16px",
    boxSizing: "border-box",
  },
  card: {
    background: "#fff",
    padding: "30px",
    borderRadius: "16px",
    width: "100%",
    maxWidth: "400px",
    boxSizing: "border-box",
    boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
  },
  title: {
    marginBottom: "10px",
  },
  text: {
    marginBottom: "15px",
  },
  list: {
    marginBottom: "20px",
  },
  buttonRow: {
    display: "flex",
    justifyContent: "space-between",
  },
  yesButton: {
    background: "#356dcb",
    color: "#fff",
    padding: "10px 15px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
  noButton: {
    background: "#e2e8f0",
    padding: "10px 15px",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
};