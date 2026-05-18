import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import axios from "axios";
import { apiRequest } from "./authConfig";

import { API_BASE_URL } from "./config";
import { useIsMobile } from "./useIsMobile";

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

export default function EpisodePage() {
  const { episodeNumber } = useParams();
  const navigate = useNavigate();
  const { instance, accounts } = useMsal();
  const isMobile = useIsMobile();

  const [episode, setEpisode] = useState(null);
  const [showTranscript, setShowTranscript] = useState(true);
  const [fullTranscript, setFullTranscript] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  const [quizAnswer, setQuizAnswer] = useState("");
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [savingQuiz, setSavingQuiz] = useState(false);

  const [savingReaction, setSavingReaction] = useState(false);
  const [reactionPopup, setReactionPopup] = useState(null);
  const [localReactions, setLocalReactions] = useState([]);
  const [audioDuration, setAudioDuration] = useState(0);

  const startedAtRef = useRef(null);
  const audioRef = useRef(null);
  const popupTimerRef = useRef(null);
  const activeSegmentRef = useRef(null);

  const toSeconds = (time) => {
    const [h, m, s] = time.replace(",", ".").split(":");
    return parseFloat(h) * 3600 + parseFloat(m) * 60 + parseFloat(s);
  };

  const getApiToken = async () => {
    const account = instance.getActiveAccount() || accounts[0];

    if (!account) {
      throw new Error("No active account found");
    }

    const response = await instance.acquireTokenSilent({
      ...apiRequest,
      account,
    });

    return response.accessToken;
  };

  const loadEpisode = async () => {
    try {
      const token = await getApiToken();

      const res = await axios.get(
        `${API_BASE_URL}/episodes/${episodeNumber}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setEpisode(res.data);

      const parsedTranscript = res.data.transcript.map((seg, index) => ({
        id: index,
        text: seg.text.replace(/\n/g, " "),
        startSec: toSeconds(seg.start),
        endSec: toSeconds(seg.end),
      }));

      setFullTranscript(parsedTranscript);

      await axios.post(
        `${API_BASE_URL}/episodes/${episodeNumber}/start`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      startedAtRef.current = Date.now();
    } catch (err) {
      console.error("Failed to load episode:", err);
    }
  };

  const submitQuizResponse = async (skipped = false) => {
    try {
      setSavingQuiz(true);
      const token = await getApiToken();

      await axios.post(
        `${API_BASE_URL}/episodes/${episodeNumber}/quiz-response`,
        {
          question_text: currentQuestion?.question || null,
          response_text: skipped ? null : quizAnswer,
          skipped,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setQuizSubmitted(true);
    } catch (err) {
      console.error("Failed to save quiz response:", err);
    } finally {
      setSavingQuiz(false);
    }
  };

  const showReactionPopup = (emoji, currentTime) => {
    if (popupTimerRef.current) clearTimeout(popupTimerRef.current);

    const minutes = Math.floor(currentTime / 60);
    const seconds = String(currentTime % 60).padStart(2, "0");

    setReactionPopup({
      emoji,
      text: `Saved at ${minutes}:${seconds}`,
    });

    popupTimerRef.current = setTimeout(() => {
      setReactionPopup(null);
    }, 1800);
  };

  const submitReaction = async (emoji) => {
    try {
      const audio = audioRef.current;
      const currentTime = audio ? Math.floor(audio.currentTime) : 0;

      showReactionPopup(emoji, currentTime);
      setLocalReactions((prev) => [...prev, { emoji, timestamp: currentTime }]);
      setSavingReaction(true);

      const token = await getApiToken();

      await axios.post(
        `${API_BASE_URL}/episodes/${episodeNumber}/reaction`,
        {
          emoji,
          audio_timestamp_seconds: currentTime,
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
    } catch (err) {
      console.error("Failed to save reaction:", err);
    } finally {
      setSavingReaction(false);
    }
  };

  const markComplete = async () => {
    try {
      const token = await getApiToken();

      const startedAt = startedAtRef.current || Date.now();
      const timeSpentSeconds = Math.floor((Date.now() - startedAt) / 1000);

      await axios.post(
        `${API_BASE_URL}/episodes/${episodeNumber}/complete`,
        { time_spent_seconds: timeSpentSeconds },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      navigate("/");
    } catch (err) {
      console.error("Failed to complete episode:", err);
    }
  };

  useEffect(() => {
    loadEpisode();
  }, [episodeNumber]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || fullTranscript.length === 0) return;

    const interval = setInterval(() => {
      const currentTime = audio.currentTime;

      const index = fullTranscript.findIndex(
        (seg) => currentTime >= seg.startSec && currentTime <= seg.endSec
      );

      if (index !== -1) {
        setCurrentIndex(index);
      }
    }, 200);

    return () => clearInterval(interval);
  }, [fullTranscript]);

  useEffect(() => {
    activeSegmentRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [currentIndex]);

  useEffect(() => {
    return () => {
      if (popupTimerRef.current) clearTimeout(popupTimerRef.current);
    };
  }, []);

  if (!episode) {
    return (
      <div style={styles.loadingPage}>
        <div style={styles.loadingCard}>Loading episode...</div>
      </div>
    );
  }

  const currentQuestion = episode.quiz?.[0];
  const headerImage =
    episode.image_url || episodeImages[Number(episodeNumber)] || episodeImages[2];

  return (
    <div style={{...styles.page, padding: isMobile ? "12px" : "28px"}}>
      <div style={styles.container}>
        <div style={styles.topBar}>
          <button style={styles.backButton} onClick={() => navigate("/")}>
            ← Back to Dashboard
          </button>

          <div style={styles.progressBadge}>Episode {episodeNumber}</div>
        </div>

        <div style={styles.headerCard}>
          {!isMobile && (
            <div style={styles.headerImageArea}>
              <img
                src={headerImage}
                alt={`Episode ${episodeNumber}`}
                style={styles.headerImage}
              />
              <div style={styles.headerImageFade}></div>
            </div>
          )}

          <div style={{...styles.headerText, width: isMobile ? "100%" : "58%"}}>
            <div style={styles.tag}>Weekly learning episode</div>
            <h1 style={{...styles.title, fontSize: isMobile ? "24px" : "40px"}}>{episode.title}</h1>

            {episode.description ? (
              <p style={styles.description}>{episode.description}</p>
            ) : null}
          </div>
        </div>

        <div
          style={{
            ...styles.layout,
            gridTemplateColumns: isMobile || !showTranscript ? "1fr" : "0.95fr 1.4fr",
          }}
        >
          {showTranscript && (
            <div style={{...styles.transcriptPanel, order: isMobile ? 1 : 0, position: isMobile ? "static" : "sticky"}}>
              <div style={styles.transcriptHeader}>
                <h3 style={styles.transcriptTitle}>Transcript</h3>
                <p style={styles.transcriptSub}>
                  Read along while listening. The transcript scrolls automatically.
                </p>
              </div>

              <div style={styles.transcriptBody}>
                {fullTranscript.length > 0 ? (
                 <div style={styles.transcriptContainer}>
  {fullTranscript.map((seg, idx) => (
    <div
      key={idx}
      ref={idx === currentIndex ? activeSegmentRef : null}
      style={{
        ...styles.transcriptBlock,
        ...(idx === currentIndex ? styles.transcriptBlockActive : {}),
      }}
    >
      {seg.text}
    </div>
  ))}
</div>
                ) : (
                  <div>No transcript available.</div>
                )}
              </div>
            </div>
          )}

          <div style={{...styles.mainColumn, order: isMobile ? 0 : 1}}>
            <div style={styles.audioCard}>
              <div style={styles.sectionHeader}>
                <div>
                  <h2 style={styles.sectionTitle}>Listen to this episode</h2>
                  <p style={styles.sectionSub}>
                    Play the audio below and continue at your own pace.
                  </p>
                </div>

                <button
                  onClick={() => setShowTranscript(!showTranscript)}
                  style={styles.secondaryButton}
                >
                  {showTranscript ? "Hide Transcript" : "Show Transcript"}
                </button>
              </div>

              <div style={styles.audioWrapper}>
                {localReactions.length > 0 && audioDuration > 0 && (
                  <div style={styles.emojiTimeline}>
                    <div style={styles.emojiTimelineLine} />
                    {localReactions.map((r, i) => (
                      <span
                        key={i}
                        title={`${Math.floor(r.timestamp / 60)}:${String(r.timestamp % 60).padStart(2, "0")}`}
                        style={{
                          ...styles.emojiTimelineMarker,
                          left: `${Math.min((r.timestamp / audioDuration) * 100, 97)}%`,
                        }}
                      >
                        {r.emoji}
                      </span>
                    ))}
                  </div>
                )}
                <audio
                  ref={audioRef}
                  controls
                  style={styles.audioPlayer}
                  onLoadedMetadata={(e) => setAudioDuration(e.target.duration)}
                >
                  <source src={episode.audio_url} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>

              <div style={styles.reactionCard}>
                <p style={styles.reactionTitle}>
                  React at any moment while listening
                </p>

                <div style={styles.reactionPopupArea}>
                  {reactionPopup && (
                    <div style={styles.reactionPopup}>
                      <span style={styles.reactionPopupEmoji}>
                        {reactionPopup.emoji}
                      </span>
                      <span>{reactionPopup.text}</span>
                    </div>
                  )}
                </div>

                <div style={styles.reactionRow}>
                  {["😊", "😐", "😢", "👍", "❤️"].map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => submitReaction(emoji)}
                      disabled={savingReaction}
                      style={styles.emojiButton}
                    >
                      <span style={styles.emojiButtonIcon}>{emoji}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {currentQuestion && (
              <div style={styles.quizCard}>
                <div style={styles.quizTop}>
                  <div style={styles.quizBadge}>Optional Reflection</div>
                </div>

                <h3 style={styles.questionText}>{currentQuestion.question}</h3>

                {!quizSubmitted ? (
                  <>
                    <textarea
                      value={quizAnswer}
                      onChange={(e) => setQuizAnswer(e.target.value)}
                      placeholder="Type your response here..."
                      style={styles.textArea}
                    />

                    <div style={styles.quizActionRow}>
                      <button
                        onClick={() => submitQuizResponse(false)}
                        style={styles.primaryButton}
                        disabled={!quizAnswer.trim() || savingQuiz}
                      >
                        {savingQuiz ? "Saving..." : "Save Response"}
                      </button>

                      <button
                        onClick={() => submitQuizResponse(true)}
                        style={styles.secondaryFinishButton}
                        disabled={savingQuiz}
                      >
                        Skip
                      </button>
                    </div>
                  </>
                ) : (
                  <div style={styles.explanationBox}>
                    <p style={styles.explanationHeading}>Response saved</p>
                    <p style={styles.explanationText}>
                      Thank you. Your response has been recorded.
                    </p>
                  </div>
                )}
              </div>
            )}

            {!currentQuestion && (
              <div style={styles.quizCard}>
                <div style={styles.quizTop}>
                  <div style={styles.quizBadge}>No Reflection Question</div>
                </div>

                <p style={styles.explanationText}>
                  This episode does not have a reflection question. You can
                  finish the episode whenever you are ready.
                </p>
              </div>
            )}

            <div style={styles.finishCard}>
              <h3 style={styles.finishTitle}>Finish this episode</h3>
              <p style={styles.finishText}>
                When you are ready, save your progress and return to the
                dashboard.
              </p>

              <button onClick={markComplete} style={styles.continueButton}>
                Continue →
              </button>
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
    background: "linear-gradient(180deg, #eef5fb 0%, #f8fbfd 100%)",
    fontFamily: "Arial, Helvetica, sans-serif",
    padding: "28px",
  },
  container: {
    maxWidth: "1240px",
    margin: "0 auto",
  },
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
  topBar: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "12px",
    flexWrap: "wrap",
    marginBottom: "20px",
  },
  backButton: {
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "12px",
    padding: "10px 16px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
    color: "#334155",
  },
  progressBadge: {
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "999px",
    padding: "10px 14px",
    fontSize: "13px",
    fontWeight: "700",
    color: "#2858a6",
  },
  headerCard: {
    position: "relative",
    minHeight: "170px",
    background:
      "radial-gradient(circle at top left, rgba(95,184,143,0.15), transparent 28%), linear-gradient(180deg, #f6fbff 0%, #eef6fb 100%)",
    border: "1px solid #e4eef6",
    borderRadius: "28px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.06)",
    marginBottom: "24px",
    overflow: "hidden",
  },
  headerImageArea: {
    position: "absolute",
    top: 0,
    right: 0,
    bottom: 0,
    width: "42%",
    overflow: "hidden",
  },
  headerImage: {
    width: "100%",
    height: "100%",
    objectFit: "cover",
    display: "block",
  },
  headerImageFade: {
    position: "absolute",
    inset: 0,
    background:
      "linear-gradient(to right, rgba(238,246,251,0.98) 0%, rgba(238,246,251,0.94) 20%, rgba(238,246,251,0.76) 38%, rgba(238,246,251,0.22) 60%, rgba(238,246,251,0) 100%)",
  },
  headerText: {
    position: "relative",
    zIndex: 2,
    width: "58%",
    padding: "32px",
    boxSizing: "border-box",
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
    marginBottom: "18px",
  },
  title: {
    fontSize: "40px",
    lineHeight: "1.15",
    margin: "0 0 12px 0",
    color: "#0f172a",
  },
  description: {
    fontSize: "17px",
    lineHeight: "1.7",
    color: "#64748b",
    margin: 0,
  },
  layout: {
    display: "grid",
    gap: "24px",
    alignItems: "start",
  },
  mainColumn: {
    display: "grid",
    gap: "20px",
  },
  audioCard: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "24px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.05)",
  },
  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "16px",
    flexWrap: "wrap",
    marginBottom: "18px",
  },
  sectionTitle: {
    margin: "0 0 6px 0",
    fontSize: "24px",
    color: "#0f172a",
  },
  sectionSub: {
    margin: 0,
    fontSize: "14px",
    color: "#64748b",
    lineHeight: "1.5",
  },
  secondaryButton: {
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "12px",
    padding: "10px 14px",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "600",
    color: "#334155",
  },
  audioWrapper: {
    background: "#f8fbfe",
    border: "1px solid #dce9f5",
    borderRadius: "18px",
    padding: "16px",
  },
  audioPlayer: {
    width: "100%",
  },
  emojiTimeline: {
    position: "relative",
    height: "36px",
    marginBottom: "8px",
  },
  emojiTimelineLine: {
    position: "absolute",
    top: "50%",
    left: 0,
    right: 0,
    height: "2px",
    background: "#dce9f5",
    borderRadius: "2px",
    transform: "translateY(-50%)",
  },
  emojiTimelineMarker: {
    position: "absolute",
    top: "50%",
    transform: "translate(-50%, -50%)",
    fontSize: "20px",
    lineHeight: 1,
    cursor: "default",
    userSelect: "none",
  },
  reactionCard: {
    marginTop: "16px",
    background: "#f8fbfe",
    border: "1px solid #dce9f5",
    borderRadius: "18px",
    padding: "16px",
  },
  reactionTitle: {
    margin: "0 0 12px 0",
    fontSize: "15px",
    fontWeight: "700",
    color: "#0f172a",
  },
  reactionPopupArea: {
    minHeight: "42px",
    marginBottom: "8px",
  },
  reactionPopup: {
    display: "inline-flex",
    alignItems: "center",
    gap: "10px",
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "999px",
    padding: "10px 14px",
    fontSize: "13px",
    fontWeight: "600",
    color: "#334155",
    boxShadow: "0 10px 22px rgba(31, 41, 55, 0.08)",
  },
  reactionPopupEmoji: {
    fontSize: "18px",
    lineHeight: 1,
  },
  reactionRow: {
    display: "flex",
    gap: "10px",
    flexWrap: "wrap",
  },
  emojiButton: {
    fontSize: "24px",
    background: "#ffffff",
    border: "1px solid #d7e3ee",
    borderRadius: "12px",
    padding: "10px 14px",
    cursor: "pointer",
    minWidth: "54px",
  },
  emojiButtonIcon: {
    display: "inline-block",
  },
  quizCard: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "24px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.05)",
  },
  quizTop: {
    marginBottom: "16px",
  },
  quizBadge: {
    display: "inline-block",
    background: "#eef4ff",
    border: "1px solid #d6e3ff",
    color: "#2858a6",
    borderRadius: "999px",
    padding: "8px 12px",
    fontSize: "13px",
    fontWeight: "700",
  },
  questionText: {
    margin: "0 0 18px 0",
    fontSize: "22px",
    lineHeight: "1.45",
    color: "#0f172a",
  },
  textArea: {
    width: "100%",
    minHeight: "120px",
    padding: "14px",
    borderRadius: "14px",
    border: "1px solid #d8e3ed",
    fontSize: "15px",
    color: "#1f2937",
    resize: "vertical",
    outline: "none",
    boxSizing: "border-box",
  },
  explanationBox: {
    marginTop: "20px",
    padding: "18px",
    borderRadius: "16px",
    backgroundColor: "#f8fbfe",
    border: "1px solid #dce9f5",
  },
  explanationHeading: {
    margin: "0 0 8px 0",
    fontSize: "16px",
    fontWeight: "700",
    color: "#0f172a",
  },
  explanationText: {
    margin: "0 0 16px 0",
    fontSize: "14px",
    lineHeight: "1.6",
    color: "#64748b",
  },
  quizActionRow: {
    display: "flex",
    gap: "12px",
    marginTop: "20px",
    flexWrap: "wrap",
  },
  finishCard: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "24px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.05)",
  },
  finishTitle: {
    margin: "0 0 8px 0",
    fontSize: "20px",
    color: "#0f172a",
  },
  finishText: {
    margin: "0 0 18px 0",
    fontSize: "14px",
    lineHeight: "1.6",
    color: "#64748b",
  },
  primaryButton: {
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
  continueButton: {
    width: "100%",
    background: "#356dcb",
    color: "#ffffff",
    border: "none",
    borderRadius: "18px",
    padding: "20px 24px",
    fontSize: "22px",
    fontWeight: "800",
    cursor: "pointer",
    boxShadow: "0 12px 28px rgba(53,109,203,0.35)",
    letterSpacing: "0.3px",
  },
  transcriptContainer: {
  display: "flex",
  flexDirection: "column",
  gap: "10px",
},

transcriptBlock: {
  padding: "8px 10px",
  borderRadius: "8px",
  lineHeight: "1.6",
  fontSize: "15px",
  transition: "all 0.2s ease",
},

transcriptBlockActive: {
  backgroundColor: "#dbeafe",
  fontWeight: "600",
  color: "#0f172a",
},
  secondaryFinishButton: {
    background: "#ffffff",
    color: "#334155",
    border: "1px solid #d7e3ee",
    borderRadius: "14px",
    padding: "13px 18px",
    fontSize: "15px",
    fontWeight: "700",
    cursor: "pointer",
  },
  transcriptPanel: {
    background: "#ffffff",
    border: "1px solid #e3ecf4",
    borderRadius: "24px",
    padding: "24px",
    boxShadow: "0 12px 32px rgba(31, 41, 55, 0.05)",
    position: "sticky",
    top: "24px",
    maxHeight: "75vh",
    overflow: "hidden",
  },
  transcriptHeader: {
    marginBottom: "14px",
  },
  transcriptTitle: {
    margin: "0 0 6px 0",
    fontSize: "22px",
    color: "#0f172a",
  },
  transcriptSub: {
    margin: 0,
    fontSize: "14px",
    color: "#64748b",
    lineHeight: "1.5",
  },
  transcriptBody: {
    maxHeight: "58vh",
    overflowY: "auto",
    lineHeight: "1.8",
    fontSize: "16px",
    color: "#334155",
    paddingRight: "6px",
  },
  transcriptParagraph: {
    margin: 0,
    lineHeight: "1.9",
    fontSize: "16px",
    color: "#334155",
  },
  transcriptTextChunk: {
    cursor: "pointer",
    transition: "all 0.2s ease",
  },
  transcriptTextChunkActive: {
    backgroundColor: "#dbeafe",
    padding: "2px 5px",
    borderRadius: "6px",
    fontWeight: "700",
    color: "#0f172a",
  },
};