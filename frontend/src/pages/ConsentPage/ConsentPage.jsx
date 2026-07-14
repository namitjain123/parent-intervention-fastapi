import { useState } from "react";
import styles from "./ConsentPage.module.css";

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
    <div className={styles.container}>
      <div className={styles.card}>
        <h2 className={styles.title}>Participant Consent</h2>

        <p className={styles.text}>
          Before you begin, please confirm your consent to participate in this
          research program.
        </p>

        <ul className={styles.list}>
          <li>Your participation is voluntary</li>
          <li>Your data will be securely stored and anonymised</li>
          <li>You may withdraw at any time</li>
        </ul>

        <div className={styles.buttonRow}>
          <button className={styles.noButton} onClick={handleNo}>
            No, I do not consent
          </button>

          <button className={styles.yesButton} onClick={handleYes}>
            Yes, I consent
          </button>
        </div>

        {loading && <p>Redirecting...</p>}
      </div>
    </div>
  );
}
