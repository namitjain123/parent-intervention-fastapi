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
    <div style={styles.page}>
      <div style={styles.shell}>
        <div style={styles.hero}>
          <div style={styles.brand}>
            <span style={styles.brandDot}></span>
            Parenting Intervention Platform
          </div>

          <h1 style={styles.heroTitle}>
            Support your child’s online safety with simple weekly guidance.
          </h1>

          <p style={styles.lead}>
            A secure research platform for Australian parents and caregivers of
            adolescents. Learn through short episodes, practical activities, and
            guided reflection at your own pace.
          </p>

          <div style={styles.illustrationCard}>
            <div>
              <h3 style={styles.illustrationHeading}>
                Built for clarity, trust, and support
              </h3>
              <p style={styles.illustrationText}>
                This platform helps parents strengthen knowledge, confidence,
                and communication around adolescents’ online privacy and
                security.
              </p>
            </div>

            <svg
              viewBox="0 0 320 240"
              xmlns="http://www.w3.org/2000/svg"
              style={styles.art}
              aria-label="Parent and child illustration"
            >
              <rect width="320" height="240" rx="24" fill="#edf6ff" />
              <circle cx="237" cy="54" r="24" fill="#d8ebff" />
              <rect
                x="44"
                y="132"
                width="118"
                height="58"
                rx="12"
                fill="#ffffff"
                stroke="#d6e6f5"
              />
              <rect
                x="72"
                y="88"
                width="118"
                height="70"
                rx="14"
                fill="#356dcb"
                opacity="0.12"
              />
              <rect
                x="78"
                y="96"
                width="106"
                height="56"
                rx="10"
                fill="#ffffff"
              />
              <rect
                x="88"
                y="106"
                width="44"
                height="8"
                rx="4"
                fill="#bdd6f8"
              />
              <rect
                x="88"
                y="122"
                width="70"
                height="8"
                rx="4"
                fill="#d6e6f8"
              />
              <rect
                x="88"
                y="138"
                width="58"
                height="8"
                rx="4"
                fill="#d6e6f8"
              />
              <circle cx="215" cy="119" r="32" fill="#ffd9bf" />
              <rect
                x="187"
                y="148"
                width="56"
                height="58"
                rx="18"
                fill="#5fb88f"
              />
              <circle cx="142" cy="132" r="25" fill="#ffd9bf" />
              <rect
                x="122"
                y="157"
                width="42"
                height="49"
                rx="14"
                fill="#f1b24a"
              />
              <path
                d="M115 111c8-20 41-24 52-4 3 6 2 12-1 16h-46c-5-4-8-8-5-12z"
                fill="#374151"
              />
              <path
                d="M190 95c8-22 40-24 51-2 3 6 3 13-1 18h-46c-7-6-7-11-4-16z"
                fill="#1f2937"
              />
              <rect
                x="235"
                y="151"
                width="32"
                height="10"
                rx="5"
                fill="#7dc6a3"
              />
              <rect
                x="229"
                y="167"
                width="44"
                height="10"
                rx="5"
                fill="#7dc6a3"
              />
              <rect
                x="224"
                y="183"
                width="54"
                height="10"
                rx="5"
                fill="#7dc6a3"
              />
            </svg>
          </div>

          <div style={styles.imageStripSection}>
            <div style={styles.imageStrip}>
              <div style={styles.imageCard}>
                <img
                  src="https://images.unsplash.com/photo-1516627145497-ae6968895b74?auto=format&fit=crop&w=900&q=80"
                  alt="Parent and child using a laptop"
                  style={styles.stripImage}
                />
                <div style={styles.imageOverlay}></div>
              </div>

              <div style={styles.imageCard}>
                <img
                  src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=900&q=80"
                  alt="Teen learning online"
                  style={styles.stripImage}
                />
                <div style={styles.imageOverlay}></div>
              </div>

              <div style={styles.imageCard}>
                <img
                  src="https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=900&q=80"
                  alt="Parent supporting child"
                  style={styles.stripImage}
                />
                <div style={styles.imageOverlay}></div>
              </div>

              <div style={styles.imageCard}>
                <img
                  src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80"
                  alt="Family discussion and guidance"
                  style={styles.stripImage}
                />
                <div style={styles.imageOverlay}></div>
              </div>
            </div>
          </div>
        </div>

        <div style={styles.auth}>
          <div style={styles.authCard}>
            <div style={styles.topNote}>
              Secure access for registered study participants
            </div>

            <div style={styles.panel}>
              <h2 style={styles.panelTitle}>Welcome</h2>

              <div style={styles.secureBanner}>
                <span style={styles.secureIcon}>🔒</span>
                Your account and study data are protected with secure
                authentication.
              </div>

              <button style={styles.primaryBtn} onClick={handleLogin}>
                Log in
              </button>

              <p style={styles.note}>
                You will be able to sign in or create an account in the next
                step.
              </p>

              <div style={styles.trustRow}>
                <div style={styles.trustItem}>
                  <strong>Secure login</strong>
                  <span>Protected participant access</span>
                </div>
                <div style={styles.trustItem}>
                  <strong>Mobile friendly</strong>
                  <span>Works on phone, tablet, and desktop</span>
                </div>
                <div style={styles.trustItem}>
                  <strong>Research study</strong>
                  <span>Designed for monitored trial delivery</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "24px",
    background: "linear-gradient(180deg, #eef5fb 0%, #f8fbfd 100%)",
    fontFamily: "Arial, Helvetica, sans-serif",
    boxSizing: "border-box",
  },
  shell: {
    width: "100%",
    maxWidth: "1220px",
    background: "#ffffff",
    borderRadius: "28px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.12)",
    overflow: "hidden",
    border: "1px solid #eaf0f6",
    display: "grid",
    gridTemplateColumns: "1.1fr 0.9fr",
  },
  hero: {
    padding: "56px 52px",
    background:
      "radial-gradient(circle at top left, rgba(95,184,143,0.18), transparent 28%), radial-gradient(circle at bottom right, rgba(53,109,203,0.14), transparent 30%), linear-gradient(180deg, #f6fbff 0%, #eef6fb 100%)",
  },
  brand: {
    display: "inline-flex",
    alignItems: "center",
    gap: "10px",
    background: "rgba(255,255,255,0.8)",
    border: "1px solid #d7e4f0",
    padding: "8px 14px",
    borderRadius: "999px",
    fontSize: "14px",
    color: "#2858a6",
    fontWeight: "bold",
  },
  brandDot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    background: "#5fb88f",
    display: "inline-block",
  },
  heroTitle: {
    fontSize: "42px",
    lineHeight: "1.16",
    margin: "24px 0 16px",
    maxWidth: "600px",
    color: "#1f2937",
  },
  lead: {
    fontSize: "18px",
    lineHeight: "1.6",
    color: "#6b7280",
    maxWidth: "620px",
    marginBottom: "28px",
  },
  illustrationCard: {
    background: "rgba(255,255,255,0.92)",
    border: "1px solid #dfebf4",
    borderRadius: "24px",
    padding: "22px",
    display: "grid",
    gridTemplateColumns: "1.2fr 0.8fr",
    gap: "18px",
    alignItems: "center",
    marginBottom: "28px",
  },
  illustrationHeading: {
    margin: "0 0 8px",
    fontSize: "22px",
    color: "#1f2937",
  },
  illustrationText: {
    margin: 0,
    color: "#6b7280",
    lineHeight: "1.55",
    fontSize: "15px",
  },
  art: {
    width: "100%",
    height: "auto",
    display: "block",
    borderRadius: "20px",
    background: "#edf6ff",
  },
  imageStripSection: {
    marginTop: "8px",
  },
  imageStrip: {
    display: "grid",
    gridTemplateColumns: "repeat(4, 1fr)",
    gap: "0",
    borderRadius: "22px",
    overflow: "hidden",
    border: "1px solid #dfe8f2",
    boxShadow: "0 10px 28px rgba(31, 41, 55, 0.08)",
  },
  imageCard: {
    position: "relative",
    minHeight: "190px",
    overflow: "hidden",
  },
  stripImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },
  imageOverlay: {
    position: "absolute",
    inset: 0,
    background:
      "linear-gradient(180deg, rgba(12, 18, 28, 0.08) 0%, rgba(12, 18, 28, 0.18) 100%)",
    pointerEvents: "none",
  },
  auth: {
    padding: "44px 36px",
    background: "#ffffff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  authCard: {
    width: "100%",
    maxWidth: "420px",
  },
  topNote: {
    fontSize: "13px",
    color: "#6b7280",
    marginBottom: "18px",
  },
  panel: {
    border: "1px solid #dbe4ee",
    borderRadius: "22px",
    padding: "24px",
    background: "#fff",
  },
  panelTitle: {
    margin: "0 0 16px",
    fontSize: "30px",
    color: "#1f2937",
  },
  secureBanner: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    background: "#f5fbf7",
    border: "1px solid #d7efe0",
    color: "#235b44",
    fontSize: "14px",
    borderRadius: "14px",
    padding: "12px 14px",
    marginBottom: "18px",
    lineHeight: "1.5",
  },
  secureIcon: {
    width: "30px",
    height: "30px",
    borderRadius: "50%",
    background: "#dff4e7",
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "bold",
    flexShrink: 0,
  },
  primaryBtn: {
    width: "100%",
    border: "none",
    borderRadius: "16px",
    padding: "15px 18px",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    background: "#356dcb",
    color: "white",
  },
  note: {
    fontSize: "13px",
    marginTop: "15px",
    color: "#777",
    lineHeight: "1.5",
    textAlign: "center",
  },
  trustRow: {
    display: "grid",
    gridTemplateColumns: "repeat(3, 1fr)",
    gap: "10px",
    marginTop: "18px",
  },
  trustItem: {
    border: "1px solid #e3ebf4",
    background: "#f9fbfd",
    borderRadius: "14px",
    padding: "12px",
    textAlign: "center",
    fontSize: "12px",
    color: "#6b7280",
    lineHeight: "1.35",
    display: "flex",
    flexDirection: "column",
    gap: "4px",
  },
};