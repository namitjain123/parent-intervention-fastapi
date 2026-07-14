import { useState } from "react";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "../../config/authConfig";
import { useIsMobile } from "../../hooks/useIsMobile";
import styles from "./LoginPage.module.css";

export default function LoginPage() {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const [redcapConsent, setRedcapConsent] = useState(false);
  const [termsConsent, setTermsConsent] = useState(false);
  const [showConsentModal, setShowConsentModal] = useState(false);

  const isMobile = useIsMobile();
  const canLogin = redcapConsent && termsConsent;

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  const openConsentForm = () => {
    window.open("/online-consent.pdf", "_blank");
  };

  if (isAuthenticated) return null;

  return (
    <div
      className={styles.page}
      style={{ padding: isMobile ? "12px" : "24px", alignItems: isMobile ? "flex-start" : "center" }}
    >
      <div
        className={styles.shell}
        style={{ gridTemplateColumns: isMobile ? "1fr" : "1.1fr 0.9fr" }}
      >
        <div
          className={styles.hero}
          style={{ padding: isMobile ? "32px 20px" : "56px 52px" }}
        >
          <div className={styles.brand}>
            <span className={styles.brandDot}></span>
            Parenting Intervention Platform
          </div>

          <h1
            className={styles.heroTitle}
            style={{ fontSize: isMobile ? "26px" : "42px" }}
          >
            Support your child’s online safety with simple weekly guidance.
          </h1>

          <p className={styles.lead}>
            A secure research platform for Australian parents and caregivers of
            adolescents. Learn through short episodes, practical activities, and
            guided reflection at your own pace.
          </p>

          <div
            className={styles.illustrationCard}
            style={{ gridTemplateColumns: isMobile ? "1fr" : "1.2fr 0.8fr" }}
          >
            <ul className={styles.illustrationList}>
              <li>Help children stay safer online</li>
              <li>Respond calmly and supportively Build</li>
              <li>confidence in supporting children</li>
              <li>Strengthen parent-child</li>
            </ul>

            <svg
              viewBox="0 0 320 240"
              xmlns="http://www.w3.org/2000/svg"
              className={styles.art}
              aria-label="Parent and child illustration"
            >
              <rect width="320" height="240" rx="24" fill="#edf6ff" />
              <circle cx="237" cy="54" r="24" fill="#d8ebff" />
              <rect x="44" y="132" width="118" height="58" rx="12" fill="#ffffff" stroke="#d6e6f5" />
              <rect x="72" y="88" width="118" height="70" rx="14" fill="#356dcb" opacity="0.12" />
              <rect x="78" y="96" width="106" height="56" rx="10" fill="#ffffff" />
              <rect x="88" y="106" width="44" height="8" rx="4" fill="#bdd6f8" />
              <rect x="88" y="122" width="70" height="8" rx="4" fill="#d6e6f8" />
              <rect x="88" y="138" width="58" height="8" rx="4" fill="#d6e6f8" />
              <circle cx="215" cy="119" r="32" fill="#ffd9bf" />
              <rect x="187" y="148" width="56" height="58" rx="18" fill="#5fb88f" />
              <circle cx="142" cy="132" r="25" fill="#ffd9bf" />
              <rect x="122" y="157" width="42" height="49" rx="14" fill="#f1b24a" />
              <path d="M115 111c8-20 41-24 52-4 3 6 2 12-1 16h-46c-5-4-8-8-5-12z" fill="#374151" />
              <path d="M190 95c8-22 40-24 51-2 3 6 3 13-1 18h-46c-7-6-7-11-4-16z" fill="#1f2937" />
              <rect x="235" y="151" width="32" height="10" rx="5" fill="#7dc6a3" />
              <rect x="229" y="167" width="44" height="10" rx="5" fill="#7dc6a3" />
              <rect x="224" y="183" width="54" height="10" rx="5" fill="#7dc6a3" />
            </svg>
          </div>

          <div className={styles.imageStripSection}>
            <div className={styles.imageStrip}>
              <div className={styles.imageCard}>
                <img src="/episode%206.jpg" alt="Parenting support" className={styles.stripImage} />
                <div className={styles.imageOverlay}></div>
              </div>
            </div>
          </div>
        </div>

        <div
          className={styles.auth}
          style={{ padding: isMobile ? "20px 16px" : "44px 36px" }}
        >
          <div className={styles.authCard}>
            <div className={styles.topNote}>

            </div>

            <div className={styles.panel}>
              <h2 className={styles.panelTitle}>Welcome</h2>

              <div className={styles.secureBanner}>
                <span className={styles.secureIcon}>🔒</span>
                Your account and study data are protected with secure authentication.
              </div>

              <div className={styles.checkboxBox}>
                <label className={styles.checkboxRow}>
                  <input
                    type="checkbox"
                    checked={redcapConsent}
                    onChange={(e) => setRedcapConsent(e.target.checked)}
                  />
                  <span>
                    Open and review the{" "}
                    <button type="button" className={styles.linkButton} onClick={openConsentForm}>
                      participation letter
                    </button>
                  </span>
                </label>

                <div className={styles.checkboxRow}>
                  <input type="checkbox" checked={termsConsent} readOnly />
                  <span>
                    I have read the{" "}
                    <button
                      type="button"
                      className={styles.linkButton}
                      onClick={() => setShowConsentModal(true)}
                    >
                      consent form
                    </button>
                  </span>
                </div>
              </div>

              {canLogin ? (
                <button className={styles.primaryBtn} onClick={handleLogin}>
                  Log in
                </button>
              ) : (
                <p className={styles.note}>
                  Please complete both consent steps to continue.
                </p>
              )}

              <p className={styles.qaRow}>
                Have a question?{" "}
                <a
                  href="/qa.pdf"
                  target="_blank"
                  rel="noopener noreferrer"
                  className={styles.linkButton}
                >
                  Read our Q&amp;A
                </a>
              </p>

            </div>
          </div>
        </div>
      </div>

      {showConsentModal && (
        <div className={styles.modalOverlay} onClick={() => setShowConsentModal(false)}>
          <div className={styles.modalCard} onClick={(e) => e.stopPropagation()}>
            <div className={styles.modalHeader}>
              <h2 className={styles.modalTitle}>Consent Form – Survey</h2>
              <button
                type="button"
                className={styles.modalClose}
                onClick={() => setShowConsentModal(false)}
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className={styles.modalContent}>
              <h3 className={styles.modalSubTitle}>Declaration by the participant</h3>

              <ul className={styles.consentList}>
                <li>
                  I have read the Participant Information Sheet, or someone has read it to me in a
                  language that I understand. I have had an opportunity to ask questions, and I am
                  satisfied with the answers I have received. I understand the purposes, study tasks
                  and risks of the research described in the study and understand that I am free to
                  withdraw at any time during the study, and withdrawal will not affect my
                  relationship with the research team members.
                </li>
                <li>
                  I understand I am agreeing to participate in the online survey as outlined in the
                  Participant Information Sheet.
                </li>
                <li>
                  I understand that data analysis will be conducted using research software tools
                  (e.g. statistical software, qualitative analysis programs, and AI-assisted tools)
                  for the purposes of analysing patterns and themes in de-identified data only,
                  within the university’s secure systems.
                </li>
                <li>
                  I may exit the survey at any time by closing the survey ‘window’ on my device and
                  there is no obligation to answer all questions or finish the survey. If I exit the
                  survey before submitting my responses, my responses will not be included in the
                  research.
                </li>
                <li>
                  I understand that I can withdraw from the study at any time before submitting the
                  survey. Once my responses are submitted, they cannot be withdrawn because they are
                  collected anonymously and do not contain identifying information.
                </li>
              </ul>

              <p className={styles.boldText}>
                Clicking ‘Yes, I agree to participate’ below, I consent to take part in this study.
              </p>
            </div>

            <div className={styles.modalActions}>
              <button
                type="button"
                className={styles.secondaryBtn}
                onClick={() => setShowConsentModal(false)}
              >
                Cancel
              </button>

              <button
                type="button"
                className={styles.modalPrimaryBtn}
                onClick={() => {
                  setTermsConsent(true);
                  setShowConsentModal(false);
                }}
              >
                Yes, I agree to participate
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
