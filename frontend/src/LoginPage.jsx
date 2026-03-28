import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";

export default function LoginPage() {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  if (isAuthenticated) return null;

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h1 style={styles.title}>
          Support Your Child’s Online Safety
        </h1>

        <p style={styles.subtitle}>
          A simple, guided program for parents. Secure and confidential.
        </p>

        <button style={styles.button} onClick={handleLogin}>
          Continue Securely
        </button>

        <p style={styles.note}>
          You will be able to sign in or create an account in the next step.
        </p>

        <div style={styles.trust}>
          🔒 Secure Login &nbsp; | &nbsp; 📱 Mobile Friendly &nbsp; | &nbsp; 🎓 Research Study
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#f4f8fb",
    fontFamily: "Arial",
  },
  card: {
    background: "white",
    padding: "40px",
    borderRadius: "16px",
    boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
    textAlign: "center",
    maxWidth: "420px",
  },
  title: {
    fontSize: "26px",
    marginBottom: "10px",
  },
  subtitle: {
    fontSize: "16px",
    color: "#555",
    marginBottom: "30px",
  },
  button: {
    background: "#356dcb",
    color: "white",
    padding: "14px 20px",
    border: "none",
    borderRadius: "10px",
    fontSize: "16px",
    cursor: "pointer",
    width: "100%",
  },
  note: {
    fontSize: "13px",
    marginTop: "15px",
    color: "#777",
  },
  trust: {
    marginTop: "20px",
    fontSize: "12px",
    color: "#888",
  },
};