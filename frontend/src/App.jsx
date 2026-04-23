import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import axios from "axios";
import { apiRequest } from "./authConfig";
import LoginPage from "./LoginPage";
import { useEffect, useState } from "react";
import ConsentPage from "./ConsentPage";

const episodeImages = {
  1: "https://images.unsplash.com/photo-1516627145497-ae6968895b74?auto=format&fit=crop&w=1200&q=80",
  2: "https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=1200&q=80",
  3: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
  4: "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=80",
  5: "https://images.unsplash.com/photo-1513258496099-48168024aec0?auto=format&fit=crop&w=1200&q=80",
  6: "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1200&q=80",
  7: "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=1200&q=80",
  8: "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1200&q=80",
};

export default function App() {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const [token, setToken] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [hasLoaded, setHasLoaded] = useState(false);
  const [hasConsented, setHasConsented] = useState(null);

  const getApiToken = async () => {
    let account = instance.getActiveAccount();

    if (!account && accounts.length > 0) {
      account = accounts[0];
      instance.setActiveAccount(account);
    }

    if (!account) {
      throw new Error("No active account found");
    }

    try {
      const response = await instance.acquireTokenSilent({
        ...apiRequest,
        account,
      });

      return response.accessToken;
    } catch (error) {
      console.log("Silent token failed, redirecting...", error);
      await instance.acquireTokenRedirect(apiRequest);
    }
  };

  const loadDashboard = async () => {
    try {
      const accessToken = await getApiToken();
      if (!accessToken) return;

      setToken(accessToken);

      await axios.get("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const res = await axios.get("http://127.0.0.1:8000/dashboard", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      setDashboard(res.data);
    } catch (err) {
      console.error("Dashboard load failed:", err);
    }
  };

  useEffect(() => {
    const consent = localStorage.getItem("user_consent");

    if (consent === "true") {
      setHasConsented(true);
    } else if (consent === "false") {
      setHasConsented(false);
    } else {
      setHasConsented(null);
    }
  }, []);

  useEffect(() => {
    if (window !== window.parent) return;

    if (
      !hasLoaded &&
      isAuthenticated &&
      accounts.length > 0 &&
      inProgress === "none"
    ) {
      setHasLoaded(true);
      loadDashboard();
    }
  }, [isAuthenticated, accounts, inProgress, hasLoaded]);

  const handleLogout = () => {
    instance.logoutRedirect();
  };

  const openPreQuestionnaire = async () => {
    try {
      const accessToken = token || (await getApiToken());
      if (!accessToken) return;

      const meRes = await axios.get("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const participantId = meRes.data.azure_id;
      localStorage.setItem("participant_id", participantId);

      const redcapUrl = `${
        import.meta.env.VITE_REDCAP_PREQ_URL
      }&participant_id=${encodeURIComponent(participantId)}`;

      window.location.href = redcapUrl;
    } catch (err) {
      console.error("Failed to open pre-questionnaire:", err);
    }
  };

  const openPostQuestionnaire = async () => {
    try {
      const accessToken = token || (await getApiToken());
      if (!accessToken) return;

      const meRes = await axios.get("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const participantId = meRes.data.azure_id;
      localStorage.setItem("participant_id", participantId);

      const redcapUrl = `${
        import.meta.env.VITE_REDCAP_POSTQ_URL
      }&participant_id=${encodeURIComponent(participantId)}`;

      window.location.href = redcapUrl;
    } catch (err) {
      console.error("Failed to open post-questionnaire:", err);
    }
  };

  if (hasConsented === null) {
    return <ConsentPage onConsent={setHasConsented} />;
  }

  if (hasConsented === false) {
    return (
      <div style={styles.declinePage}>
        <div style={styles.declineCard}>
          <h2 style={styles.declineTitle}>You chose not to participate</h2>
          <p style={styles.declineText}>
            You cannot continue without providing consent.
          </p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) return <LoginPage />;

  if (!dashboard) {
    return (
      <div style={styles.loadingPage}>
        <div style={styles.loadingCard}>Loading dashboard...</div>
      </div>
    );
  }

  const completedEpisodeCount =
    dashboard.episodes?.filter((ep) => ep.status === "completed").length || 0;

  const allEpisodesCompleted =
    dashboard.all_episodes_completed ?? dashboard.current_episode > 8;

  return (
    <div style={styles.page}>
      <div style={styles.container}>
        <div style={styles.topBar}>
          <div>
            <div style={styles.brand}>Parenting Platform</div>
            <div style={styles.brandSub}>Parenting Intervention Program</div>
          </div>

          <div style={styles.userSection}>
            <div style={styles.userBadge}>{dashboard.name}</div>
            <button style={styles.logoutButton} onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>

        {!dashboard.pre_questionnaire_completed ? (
          <div style={styles.heroWrapper}>
            <div style={styles.leftPanel}>
              <div style={styles.tag}>Step 1 of the program</div>

              <h1 style={styles.title}>
                Before you begin, please complete the pre-questionnaire
              </h1>

              <p style={styles.subtitle}>
                This short questionnaire is required before any learning episode
                can be accessed. It helps the research team understand your
                starting point and supports your program journey.
              </p>

              <div style={styles.infoGrid}>
                <div style={styles.infoCard}>
                  <div style={styles.infoIcon}>📝</div>
                  <div>
                    <div style={styles.infoTitle}>Short and simple</div>
                    <div style={styles.infoText}>
                      The questionnaire is designed to be easy to complete.
                    </div>
                  </div>
                </div>

                <div style={styles.infoCard}>
                  <div style={styles.infoIcon}>🔒</div>
                  <div>
                    <div style={styles.infoTitle}>Secure and confidential</div>
                    <div style={styles.infoText}>
                      Your responses are linked securely to your participant ID.
                    </div>
                  </div>
                </div>

                <div style={styles.infoCard}>
                  <div style={styles.infoIcon}>🚀</div>
                  <div>
                    <div style={styles.infoTitle}>Unlocks your program</div>
                    <div style={styles.infoText}>
                      Episode access will begin after this step is completed.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div style={styles.rightPanel}>
              <div style={styles.actionCard}>
                <div style={styles.cardTop}>
                  <div style={styles.cardBadge}>Required</div>
                  <div style={styles.estimate}>Estimated time: 5–10 mins</div>
                </div>

                <h2 style={styles.cardTitle}>Pre-questionnaire required</h2>

                <p style={styles.cardText}>
                  Please complete the pre-questionnaire before accessing any
                  episode content.
                </p>

                <button
                  style={styles.primaryButton}
                  onClick={openPreQuestionnaire}
                >
                  Start Pre-questionnaire
                </button>

                <div style={styles.noteBox}>
                  After completing this step, you will return to the platform
                  and your first available episode will be unlocked.
                </div>
              </div>

              <div style={styles.progressCard}>
                <h3 style={styles.progressTitle}>Program flow</h3>

                <div style={styles.stepItem}>
                  <span style={styles.stepDone}>✓</span>
                  <span>Account created</span>
                </div>

                <div style={styles.stepItem}>
                  <span style={styles.stepCurrent}>1</span>
                  <span>Complete pre-questionnaire</span>
                </div>

                <div style={styles.stepItem}>
                  <span style={styles.stepLocked}>2</span>
                  <span>Access Episode 1</span>
                </div>

                <div style={styles.stepItem}>
                  <span style={styles.stepLocked}>3</span>
                  <span>Continue weekly episodes</span>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div>
            <div style={styles.sectionHeaderRow}>
              <div>
                <h3 style={styles.episodesHeading}>Your Episodes</h3>
                <p style={styles.episodesSubtext}>
                  Continue your learning journey one episode at a time.
                </p>
              </div>

              <div style={styles.episodeSummaryBadge}>
                {completedEpisodeCount} completed
              </div>
            </div>

            <div style={styles.episodeGrid}>
              {dashboard.episodes.map((ep) => {
                const isLocked = ep.status === "locked";
                const isCompleted = ep.status === "completed";
                const isUnlocked = ep.status === "unlocked";
                const imageSrc =
                  ep.image_url || episodeImages[ep.episode_number];

                return (
                  <div
                    key={ep.episode_number}
                    style={{
                      ...styles.episodeCard,
                      ...(isLocked ? styles.episodeCardLocked : {}),
                      ...(isCompleted ? styles.episodeCardCompleted : {}),
                    }}
                  >
                    <div style={styles.episodeImageArea}>
                      <img
                        src={imageSrc}
                        alt={`Episode ${ep.episode_number}`}
                        style={styles.episodeImage}
                      />
                      <div style={styles.episodeImageFade}></div>
                    </div>

                    <div style={styles.episodeContent}>
                      <div style={styles.episodeTopRow}>
                        <div style={styles.episodeNumberBadge}>
                          Episode {ep.episode_number}
                        </div>

                        <div
                          style={{
                            ...styles.statusBadge,
                            ...(isLocked
                              ? styles.statusLocked
                              : isCompleted
                              ? styles.statusCompleted
                              : styles.statusUnlocked),
                          }}
                        >
                          {isLocked
                            ? "Locked"
                            : isCompleted
                            ? "Completed"
                            : "Available"}
                        </div>
                      </div>

                      <h4 style={styles.episodeTitle}>{ep.title}</h4>

                      <p style={styles.episodeDescription}>
                        {isCompleted &&
                          "You have completed this episode successfully."}
                        {isUnlocked &&
                          "This episode is ready to start. Continue when you are ready."}
                        {isLocked &&
                          "This episode will unlock after you complete the previous required step."}
                      </p>

                      <div style={styles.episodeFooter}>
                        {isUnlocked && (
                          <button
                            style={styles.openEpisodeButton}
                            onClick={() =>
                              (window.location.href = `/episodes/${ep.episode_number}`)
                            }
                          >
                            Open Episode
                          </button>
                        )}

                        {isLocked && (
                          <button style={styles.disabledEpisodeButton} disabled>
                            Locked
                          </button>
                        )}

                        {isCompleted && (
                          <button
                            style={styles.completedEpisodeButton}
                            disabled
                          >
                            Completed
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {allEpisodesCompleted && !dashboard.post_questionnaire_completed && (
              <div style={styles.postQuestionnaireCard}>
                <div style={styles.cardTop}>
                  <div style={styles.cardBadge}>Final Step</div>
                  <div style={styles.estimate}>Estimated time: 5–10 mins</div>
                </div>

                <h2 style={styles.cardTitle}>Post-questionnaire required</h2>

                <p style={styles.cardText}>
                  You have completed all 8 episodes. Please complete the final
                  post-questionnaire to finish the program.
                </p>

                <button
                  style={styles.primaryButton}
                  onClick={openPostQuestionnaire}
                >
                  Start Post-questionnaire
                </button>

                <div style={styles.noteBox}>
                  This final questionnaire helps the research team understand
                  your experience after completing the full program.
                </div>
              </div>
            )}

            {allEpisodesCompleted && dashboard.post_questionnaire_completed && (
              <div style={styles.postQuestionnaireCard}>
                <div style={styles.cardTop}>
                  <div style={styles.completedBadge}>Completed</div>
                </div>

                <h2 style={styles.cardTitle}>Program completed</h2>

                <p style={styles.cardText}>
                  Thank you. You have completed all episodes and the final
                  post-questionnaire.
                </p>

                <div style={styles.noteBox}>
                  Your participation in the program is now complete.
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  loadingPage: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(180deg, #eef5fb 0%, #f8fbfd 100%)",
    fontFamily: "Arial, Helvetica, sans-serif",
    padding: "24px",
  },
  loadingCard: {
    background: "#fff",
    border: "1px solid #e4edf5",
    borderRadius: "18px",
    padding: "24px 28px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.08)",
    fontSize: "16px",
    color: "#334155",
  },
  declinePage: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "linear-gradient(180deg, #eef5fb 0%, #f8fbfd 100%)",
    fontFamily: "Arial, Helvetica, sans-serif",
    padding: "24px",
  },
  declineCard: {
    background: "#ffffff",
    border: "1px solid #e4edf5",
    borderRadius: "20px",
    padding: "28px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.08)",
    textAlign: "center",
    maxWidth: "480px",
  },
  declineTitle: {
    margin: "0 0 10px 0",
    fontSize: "28px",
    color: "#0f172a",
  },
  declineText: {
    margin: 0,
    fontSize: "15px",
    lineHeight: "1.6",
    color: "#64748b",
  },
  page: {
    minHeight: "100vh",
    background: "linear-gradient(180deg, #eef5fb 0%, #f8fbfd 100%)",
    fontFamily: "Arial, Helvetica, sans-serif",
    padding: "28px",
  },
  container: {
    maxWidth: "1240px",
    margin: "0 auto",
  },
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "28px",
    background: "#ffffff",
    border: "1px solid #e7eef5",
    borderRadius: "22px",
    padding: "20px 24px",
    boxShadow: "0 8px 24px rgba(31, 41, 55, 0.05)",
    gap: "16px",
    flexWrap: "wrap",
  },
  brand: {
    fontSize: "30px",
    fontWeight: "700",
    color: "#0f172a",
    marginBottom: "4px",
  },
  brandSub: {
    fontSize: "14px",
    color: "#64748b",
  },
  userSection: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    flexWrap: "wrap",
  },
  userBadge: {
    background: "#f4f8fb",
    border: "1px solid #dbe6f0",
    borderRadius: "999px",
    padding: "10px 14px",
    fontSize: "14px",
    color: "#1e293b",
    fontWeight: "600",
  },
  logoutButton: {
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "12px",
    padding: "10px 16px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
    color: "#334155",
  },
  heroWrapper: {
    display: "grid",
    gridTemplateColumns: "1.2fr 0.8fr",
    gap: "24px",
    alignItems: "start",
  },
  leftPanel: {
    background:
      "radial-gradient(circle at top left, rgba(95,184,143,0.15), transparent 28%), linear-gradient(180deg, #f6fbff 0%, #eef6fb 100%)",
    border: "1px solid #e4eef6",
    borderRadius: "28px",
    padding: "36px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.06)",
  },
  tag: {
    display: "inline-block",
    background: "#ffffff",
    border: "1px solid #d8e6f2",
    borderRadius: "999px",
    padding: "8px 14px",
    fontSize: "13px",
    fontWeight: "700",
    color: "#2858a6",
    marginBottom: "20px",
  },
  title: {
    fontSize: "42px",
    lineHeight: "1.16",
    margin: "0 0 16px 0",
    color: "#1f2937",
    maxWidth: "700px",
  },
  subtitle: {
    fontSize: "18px",
    lineHeight: "1.7",
    color: "#64748b",
    marginBottom: "28px",
    maxWidth: "760px",
  },
  infoGrid: {
    display: "grid",
    gap: "14px",
  },
  infoCard: {
    display: "flex",
    alignItems: "flex-start",
    gap: "14px",
    background: "rgba(255,255,255,0.85)",
    border: "1px solid #dfeaf4",
    borderRadius: "18px",
    padding: "16px",
  },
  infoIcon: {
    width: "42px",
    height: "42px",
    borderRadius: "12px",
    background: "#edf6ff",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "20px",
    flexShrink: 0,
  },
  infoTitle: {
    fontSize: "15px",
    fontWeight: "700",
    color: "#1f2937",
    marginBottom: "4px",
  },
  infoText: {
    fontSize: "14px",
    color: "#64748b",
    lineHeight: "1.5",
  },
  rightPanel: {
    display: "grid",
    gap: "18px",
  },
  actionCard: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "24px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.06)",
  },
  postQuestionnaireCard: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "24px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.06)",
    marginTop: "24px",
  },
  cardTop: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    flexWrap: "wrap",
    marginBottom: "16px",
  },
  cardBadge: {
    background: "#fff7ed",
    color: "#c2410c",
    border: "1px solid #fed7aa",
    borderRadius: "999px",
    padding: "7px 12px",
    fontSize: "12px",
    fontWeight: "700",
  },
  completedBadge: {
    background: "#f0fdf4",
    color: "#15803d",
    border: "1px solid #86efac",
    borderRadius: "999px",
    padding: "7px 12px",
    fontSize: "12px",
    fontWeight: "700",
  },
  estimate: {
    fontSize: "13px",
    color: "#64748b",
    fontWeight: "600",
  },
  cardTitle: {
    margin: "0 0 10px 0",
    fontSize: "28px",
    color: "#0f172a",
  },
  cardText: {
    margin: "0 0 22px 0",
    fontSize: "15px",
    lineHeight: "1.6",
    color: "#64748b",
  },
  primaryButton: {
    width: "100%",
    background: "#356dcb",
    color: "#ffffff",
    border: "none",
    borderRadius: "16px",
    padding: "15px 18px",
    fontSize: "16px",
    fontWeight: "700",
    cursor: "pointer",
    boxShadow: "0 10px 22px rgba(53,109,203,0.25)",
  },
  noteBox: {
    marginTop: "16px",
    background: "#f8fbfe",
    border: "1px solid #dce9f5",
    borderRadius: "14px",
    padding: "14px",
    fontSize: "13px",
    lineHeight: "1.6",
    color: "#64748b",
  },
  progressCard: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "22px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.05)",
  },
  progressTitle: {
    margin: "0 0 14px 0",
    fontSize: "18px",
    color: "#0f172a",
  },
  stepItem: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
    padding: "10px 0",
    fontSize: "14px",
    color: "#334155",
  },
  stepDone: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    background: "#dcfce7",
    color: "#15803d",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "700",
    flexShrink: 0,
  },
  stepCurrent: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    background: "#dbeafe",
    color: "#1d4ed8",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "700",
    flexShrink: 0,
  },
  stepLocked: {
    width: "28px",
    height: "28px",
    borderRadius: "50%",
    background: "#f1f5f9",
    color: "#64748b",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontWeight: "700",
    flexShrink: 0,
  },
  sectionHeaderRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "16px",
    flexWrap: "wrap",
    marginBottom: "18px",
  },
  episodesHeading: {
    margin: "0 0 6px 0",
    fontSize: "30px",
    color: "#0f172a",
  },
  episodesSubtext: {
    margin: 0,
    fontSize: "15px",
    color: "#64748b",
    lineHeight: "1.5",
  },
  episodeSummaryBadge: {
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "999px",
    padding: "10px 14px",
    fontSize: "13px",
    fontWeight: "700",
    color: "#2858a6",
  },
  episodeGrid: {
    display: "grid",
    gap: "18px",
  },
  episodeCard: {
    position: "relative",
    minHeight: "190px",
    borderRadius: "24px",
    overflow: "hidden",
    border: "1px solid #e3ecf4",
    background: "#ffffff",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.05)",
  },
  episodeCardLocked: {
    background: "#f8fafc",
    border: "1px solid #e2e8f0",
  },
  episodeCardCompleted: {
    background: "#f8fffb",
    border: "1px solid #d8f0df",
  },
  episodeImageArea: {
    position: "absolute",
    top: 0,
    right: 0,
    bottom: 0,
    width: "42%",
    overflow: "hidden",
  },
  episodeImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },
  episodeImageFade: {
    position: "absolute",
    inset: 0,
    background:
      "linear-gradient(to right, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.94) 18%, rgba(255,255,255,0.74) 36%, rgba(255,255,255,0.24) 58%, rgba(255,255,255,0) 100%)",
  },
  episodeContent: {
    position: "relative",
    zIndex: 2,
    width: "58%",
    minHeight: "190px",
    padding: "22px",
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
  },
  episodeTopRow: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    flexWrap: "wrap",
    marginBottom: "16px",
  },
  episodeNumberBadge: {
    display: "inline-block",
    background: "#eef4ff",
    border: "1px solid #d6e3ff",
    color: "#2858a6",
    borderRadius: "999px",
    padding: "8px 12px",
    fontSize: "13px",
    fontWeight: "700",
  },
  statusBadge: {
    borderRadius: "999px",
    padding: "8px 12px",
    fontSize: "12px",
    fontWeight: "700",
  },
  statusUnlocked: {
    background: "#eff6ff",
    color: "#1d4ed8",
    border: "1px solid #bfdbfe",
  },
  statusCompleted: {
    background: "#f0fdf4",
    color: "#15803d",
    border: "1px solid #86efac",
  },
  statusLocked: {
    background: "#f1f5f9",
    color: "#64748b",
    border: "1px solid #cbd5e1",
  },
  episodeTitle: {
    margin: "0 0 10px 0",
    fontSize: "24px",
    color: "#0f172a",
  },
  episodeDescription: {
    margin: "0 0 18px 0",
    fontSize: "15px",
    color: "#64748b",
    lineHeight: "1.6",
    maxWidth: "760px",
  },
  episodeFooter: {
    display: "flex",
    justifyContent: "flex-start",
    alignItems: "center",
  },
  openEpisodeButton: {
    background: "#356dcb",
    color: "#ffffff",
    border: "none",
    borderRadius: "14px",
    padding: "13px 18px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
    boxShadow: "0 10px 22px rgba(53,109,203,0.22)",
  },
  disabledEpisodeButton: {
    background: "#e2e8f0",
    color: "#64748b",
    border: "none",
    borderRadius: "14px",
    padding: "13px 18px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "not-allowed",
  },
  completedEpisodeButton: {
    background: "#dcfce7",
    color: "#15803d",
    border: "none",
    borderRadius: "14px",
    padding: "13px 18px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "default",
  },
};