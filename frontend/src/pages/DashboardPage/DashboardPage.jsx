import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import axios from "axios";
import { apiRequest } from "../../config/authConfig";
import LoginPage from "../LoginPage/LoginPage";
import { useEffect, useState } from "react";
import { API_BASE_URL } from "../../config/config";
import { useIsMobile } from "../../hooks/useIsMobile";
import styles from "./DashboardPage.module.css";
const episodeImages = {
  1: "/episode%201.jpg",
  2: "/episode%202.jpg",
  3: "/episode%203.jpg",
  4: "/episode%204.jpg",
  5: "/episode%205.jpg",
  6: "/episode%206.jpg",
  7: "/episode%206.jpg",
  8: "/episode%206.jpg",
};

export default function DashboardPage() {
  const { instance, accounts, inProgress } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const isMobile = useIsMobile();

  const [token, setToken] = useState("");
  const [dashboard, setDashboard] = useState(null);
  const [hasLoaded, setHasLoaded] = useState(false);


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

      await axios.get(`${API_BASE_URL}/me`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const res = await axios.get(`${API_BASE_URL}/dashboard`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      setDashboard(res.data);
    } catch (err) {
      console.error("Dashboard load failed:", err);
    }
  };



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

      const meRes = await axios.get(`${API_BASE_URL}/me`, {
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
  const openDelayedQuestionnaire = async () => {
  try {
    const accessToken = token || (await getApiToken());
    if (!accessToken) return;

    const meRes = await axios.get(`${API_BASE_URL}/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    const participantId = meRes.data.azure_id;
    localStorage.setItem("participant_id", participantId);

    const delayedRedcapUrl = `${
      import.meta.env.VITE_REDCAP_DELAYED_URL
    }&participant_id=${encodeURIComponent(participantId)}`;

    window.location.href = delayedRedcapUrl;
  } catch (err) {
    console.error("Failed to open delayed questionnaire:", err);
  }
};

  const openPostQuestionnaire = async () => {
    try {
      const accessToken = token || (await getApiToken());
      if (!accessToken) return;

      const meRes = await axios.get(`${API_BASE_URL}/me`, {
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



  if (!isAuthenticated) return <LoginPage />;

  if (!dashboard) {
    return (
      <div className={styles.loadingPage}>
        <div className={styles.loadingCard}>Loading dashboard...</div>
      </div>
    );
  }

  const completedEpisodeCount =
    dashboard.episodes?.filter((ep) => ep.status === "completed").length || 0;

  const allEpisodesCompleted =
    dashboard.all_episodes_completed ?? dashboard.current_episode > 8;

  return (
    <div className={styles.page} style={{ padding: isMobile ? "12px" : "28px" }}>
      <div className={styles.container}>
        <div className={styles.topBar}>
          <div>
            <div className={styles.brand} style={{ fontSize: isMobile ? "20px" : "30px" }}>Parenting Platform</div>
            <div className={styles.brandSub}>Parenting Intervention Program</div>
          </div>

          <div className={styles.userSection}>
            <div className={styles.userBadge}>{dashboard.name}</div>
            <button className={styles.logoutButton} onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>

        {!dashboard.pre_questionnaire_completed ? (
          <div className={styles.heroWrapper} style={{ gridTemplateColumns: isMobile ? "1fr" : "1.2fr 0.8fr" }}>
            <div className={styles.leftPanel}>
              <div className={styles.tag}>Step 1 of the program</div>

              <h1 className={styles.title} style={{ fontSize: isMobile ? "24px" : "42px" }}>
                Before you begin, please complete the pre-questionnaire
              </h1>

              <p className={styles.subtitle}>
                This short questionnaire is required before any learning episode
                can be accessed. It helps the research team understand your
                starting point and supports your program journey.
              </p>

              <div className={styles.infoGrid}>
                <div className={styles.infoCard}>
                  <div className={styles.infoIcon}>📝</div>
                  <div>
                    <div className={styles.infoTitle}>Short and simple</div>
                    <div className={styles.infoText}>
                      The questionnaire is designed to be easy to complete.
                    </div>
                  </div>
                </div>

                <div className={styles.infoCard}>
                  <div className={styles.infoIcon}>🔒</div>
                  <div>
                    <div className={styles.infoTitle}>Secure and confidential</div>
                    <div className={styles.infoText}>
                      Your responses are linked securely to your participant ID.
                    </div>
                  </div>
                </div>

                <div className={styles.infoCard}>
                  <div className={styles.infoIcon}>🚀</div>
                  <div>
                    <div className={styles.infoTitle}>Unlocks your program</div>
                    <div className={styles.infoText}>
                      Episode access will begin after this step is completed.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className={styles.rightPanel}>
              <div className={styles.actionCard}>
                <div className={styles.cardTop}>
                  <div className={styles.cardBadge}>Required</div>
                  <div className={styles.estimate}>Estimated time: 5–10 mins</div>
                </div>

                <h2 className={styles.cardTitle}>Pre-questionnaire required</h2>

                <p className={styles.cardText}>
                  Please complete the pre-questionnaire before accessing any
                  episode content.
                </p>

                <button
                  className={styles.primaryButton}
                  onClick={openPreQuestionnaire}
                >
                  Start Pre-questionnaire
                </button>

                <div className={styles.noteBox}>
                  After completing this step, you will return to the platform
                  and your first available episode will be unlocked.
                </div>
              </div>

              <div className={styles.progressCard}>
                <h3 className={styles.progressTitle}>Program flow</h3>

                <div className={styles.stepItem}>
                  <span className={styles.stepDone}>✓</span>
                  <span>Account created</span>
                </div>

                <div className={styles.stepItem}>
                  <span className={styles.stepCurrent}>1</span>
                  <span>Complete pre-questionnaire</span>
                </div>

                <div className={styles.stepItem}>
                  <span className={styles.stepLocked}>2</span>
                  <span>Access Episode 1</span>
                </div>

                <div className={styles.stepItem}>
                  <span className={styles.stepLocked}>3</span>
                  <span>Continue weekly episodes</span>
                </div>
              </div>
            </div>
          </div>
        ) : dashboard.delayed_survey_locked ? (
  <div className={styles.comingSoonWrap}>
    <h1 className={styles.comingSoonText}>Coming soon....</h1>
  </div>
) : dashboard.show_delayed_survey ? (
  <div className="action-card waiting-card">
    <div className="card-badge"></div>
<h2 className="card-title">
      Episodes will be available after completing this survey.
    </h2>
    <p className="card-text">Your next survey is now available</p>



    <button className="primary-button" onClick={openDelayedQuestionnaire}>
      Start Survey
    </button>

    <div className="note-box">

    </div>
  </div>
) : (
  <div>
    <div className="section-header-row">
              <div>
                <h3 className={styles.episodesHeading}>Your Episodes</h3>
                <p className={styles.episodesSubtext}>
                  Continue your learning journey one episode at a time.
                </p>
              </div>

              <div className={styles.episodeSummaryBadge}>
                {completedEpisodeCount} completed
              </div>
            </div>

            <div className={styles.episodeGrid}>
              {dashboard.episodes.map((ep) => {
                const isLocked = ep.status === "locked";
                const isCompleted = ep.status === "completed";
                const isUnlocked = ep.status === "unlocked";
                const imageSrc =
                  ep.image_url || episodeImages[ep.episode_number];

                return (
                  <div
                    key={ep.episode_number}
                    className={`${styles.episodeCard} ${isLocked ? styles.episodeCardLocked : ""} ${isCompleted ? styles.episodeCardCompleted : ""}`}
                  >
                    {!isMobile && (
                      <div className={styles.episodeImageArea}>
                        <img
                          src={imageSrc}
                          alt={`Episode ${ep.episode_number}`}
                          className={styles.episodeImage}
                        />
                        <div className={styles.episodeImageFade}></div>
                      </div>
                    )}

                    <div className={styles.episodeContent} style={{ width: isMobile ? "100%" : "58%" }}>
                      <div className={styles.episodeTopRow}>
                        <div className={styles.episodeNumberBadge}>
                          Episode {ep.episode_number}
                        </div>

                        <div
                          className={`${styles.statusBadge} ${
                            isLocked
                              ? styles.statusLocked
                              : isCompleted
                              ? styles.statusCompleted
                              : styles.statusUnlocked
                          }`}
                        >
                          {isLocked
                            ? "Locked"
                            : isCompleted
                            ? "Completed"
                            : "Available"}
                        </div>
                      </div>

                      <h4 className={styles.episodeTitle}>{ep.title}</h4>

                      <p className={styles.episodeDescription}>
                        {isCompleted &&
                          "You have completed this episode successfully."}
                        {isUnlocked &&
                          "This episode is ready to start. Continue when you are ready."}
                        {isLocked &&
                          "This episode will unlock after you complete the previous required step."}
                      </p>

                      <div className={styles.episodeFooter}>
                        {isUnlocked && (
                          <button
                            className={styles.openEpisodeButton}
                            onClick={() =>
                              (window.location.href = `/episodes/${ep.episode_number}`)
                            }
                          >
                            Open Episode
                          </button>
                        )}

                        {isLocked && (
                          <button className={styles.disabledEpisodeButton} disabled>
                            Locked
                          </button>
                        )}

                        {isCompleted && (
                          <button
                            className={styles.completedEpisodeButton}
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
              <div className={styles.postQuestionnaireCard}>
                <div className={styles.cardTop}>
                  <div className={styles.cardBadge}>Final Step</div>
                  <div className={styles.estimate}>Estimated time: 5–10 mins</div>
                </div>

                <h2 className={styles.cardTitle}>Post-questionnaire required</h2>

                <p className={styles.cardText}>
                  You have completed all 8 episodes. Please complete the final
                  post-questionnaire to finish the program.
                </p>

                <button
                  className={styles.primaryButton}
                  onClick={openPostQuestionnaire}
                >
                  Start Post-questionnaire
                </button>

                <div className={styles.noteBox}>
                  This final questionnaire helps the research team understand
                  your experience after completing the full program.
                </div>
              </div>
            )}

            {allEpisodesCompleted && dashboard.post_questionnaire_completed && (
              <div className={styles.postQuestionnaireCard}>
                <div className={styles.cardTop}>
                  <div className={styles.completedBadge}>Completed</div>
                </div>

                <h2 className={styles.cardTitle}>Program completed</h2>

                <p className={styles.cardText}>
                  Thank you. You have completed all episodes and the final
                  post-questionnaire.
                </p>

                <div className={styles.noteBox}>
                  Your participation in the program is now complete.
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <a
        href="/qa.pdf"
        target="_blank"
        rel="noopener noreferrer"
        className={styles.qaFab}
        title="Read our Q&A"
      >
        Q&amp;A
      </a>
    </div>
  );
}
