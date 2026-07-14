import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import axios from "axios";
import { apiRequest } from "../../config/authConfig";

import { API_BASE_URL } from "../../config/config";
import { useIsMobile } from "../../hooks/useIsMobile";
import styles from "./EpisodePage.module.css";

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
      <div className={styles.loadingPage}>
        <div className={styles.loadingCard}>Loading episode...</div>
      </div>
    );
  }

  const currentQuestion = episode.quiz?.[0];
  const headerImage =
    episode.image_url || episodeImages[Number(episodeNumber)] || episodeImages[2];

  return (
    <div className={styles.page} style={{ padding: isMobile ? "12px" : "28px" }}>
      <div className={styles.container}>
        <div className={styles.topBar}>
          <button className={styles.backButton} onClick={() => navigate("/")}>
            ← Back to Dashboard
          </button>

          <div className={styles.progressBadge}>Episode {episodeNumber}</div>
        </div>

        <div className={styles.headerCard}>
          {!isMobile && (
            <div className={styles.headerImageArea}>
              <img
                src={headerImage}
                alt={`Episode ${episodeNumber}`}
                className={styles.headerImage}
              />
              <div className={styles.headerImageFade}></div>
            </div>
          )}

          <div className={styles.headerText} style={{ width: isMobile ? "100%" : "58%" }}>
            <div className={styles.tag}>Weekly learning episode</div>
            <h1 className={styles.title} style={{ fontSize: isMobile ? "24px" : "40px" }}>{episode.title}</h1>

            {episode.description ? (
              <p className={styles.description}>{episode.description}</p>
            ) : null}
          </div>
        </div>

        <div
          className={styles.layout}
          style={{
            gridTemplateColumns: isMobile || !showTranscript ? "1fr" : "0.95fr 1.4fr",
          }}
        >
          {showTranscript && (
            <div
              className={styles.transcriptPanel}
              style={{ order: isMobile ? 1 : 0, position: isMobile ? "static" : "sticky" }}
            >
              <div className={styles.transcriptHeader}>
                <h3 className={styles.transcriptTitle}>Transcript</h3>
                <p className={styles.transcriptSub}>
                  Read along while listening. The transcript scrolls automatically.
                </p>
              </div>

              <div className={styles.transcriptBody}>
                {fullTranscript.length > 0 ? (
                 <div className={styles.transcriptContainer}>
  {fullTranscript.map((seg, idx) => (
    <div
      key={idx}
      ref={idx === currentIndex ? activeSegmentRef : null}
      className={`${styles.transcriptBlock} ${idx === currentIndex ? styles.transcriptBlockActive : ""}`}
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

          <div className={styles.mainColumn} style={{ order: isMobile ? 0 : 1 }}>
            <div className={styles.audioCard}>
              <div className={styles.sectionHeader}>
                <div>
                  <h2 className={styles.sectionTitle}>Listen to this episode</h2>
                  <p className={styles.sectionSub}>
                    Play the audio below and continue at your own pace.
                  </p>
                </div>

                <button
                  onClick={() => setShowTranscript(!showTranscript)}
                  className={styles.secondaryButton}
                >
                  {showTranscript ? "Hide Transcript" : "Show Transcript"}
                </button>
              </div>

              <div className={styles.audioWrapper}>
                {localReactions.length > 0 && audioDuration > 0 && (
                  <div className={styles.emojiTimeline}>
                    <div className={styles.emojiTimelineLine} />
                    {localReactions.map((r, i) => (
                      <span
                        key={i}
                        title={`${Math.floor(r.timestamp / 60)}:${String(r.timestamp % 60).padStart(2, "0")}`}
                        className={styles.emojiTimelineMarker}
                        style={{
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
                  className={styles.audioPlayer}
                  onLoadedMetadata={(e) => setAudioDuration(e.target.duration)}
                >
                  <source src={episode.audio_url} type="audio/mpeg" />
                  Your browser does not support the audio element.
                </audio>
              </div>

              <div className={styles.reactionCard}>
                <p className={styles.reactionTitle}>
                  React at any moment while listening
                </p>

                <div className={styles.reactionPopupArea}>
                  {reactionPopup && (
                    <div className={styles.reactionPopup}>
                      <span className={styles.reactionPopupEmoji}>
                        {reactionPopup.emoji}
                      </span>
                      <span>{reactionPopup.text}</span>
                    </div>
                  )}
                </div>

                <div className={styles.reactionRow}>
                  {["😊", "😐", "😢", "👍", "❤️"].map((emoji) => (
                    <button
                      key={emoji}
                      onClick={() => submitReaction(emoji)}
                      disabled={savingReaction}
                      className={styles.emojiButton}
                    >
                      <span className={styles.emojiButtonIcon}>{emoji}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {currentQuestion && (
              <div className={styles.quizCard}>
                <div className={styles.quizTop}>
                  <div className={styles.quizBadge}>Optional Reflection</div>
                </div>

                <h3 className={styles.questionText}>{currentQuestion.question}</h3>

                {!quizSubmitted ? (
                  <>
                    <textarea
                      value={quizAnswer}
                      onChange={(e) => setQuizAnswer(e.target.value)}
                      placeholder="Type your response here..."
                      className={styles.textArea}
                    />

                    <div className={styles.quizActionRow}>
                      <button
                        onClick={() => submitQuizResponse(false)}
                        className={styles.primaryButton}
                        disabled={!quizAnswer.trim() || savingQuiz}
                      >
                        {savingQuiz ? "Saving..." : "Save Response"}
                      </button>

                      <button
                        onClick={() => submitQuizResponse(true)}
                        className={styles.secondaryFinishButton}
                        disabled={savingQuiz}
                      >
                        Skip
                      </button>
                    </div>
                  </>
                ) : (
                  <div className={styles.explanationBox}>
                    <p className={styles.explanationHeading}>Response saved</p>
                    <p className={styles.explanationText}>
                      Thank you. Your response has been recorded.
                    </p>
                  </div>
                )}
              </div>
            )}

            {!currentQuestion && (
              <div className={styles.quizCard}>
                <div className={styles.quizTop}>
                  <div className={styles.quizBadge}>No Reflection Question</div>
                </div>

                <p className={styles.explanationText}>
                  This episode does not have a reflection question. You can
                  finish the episode whenever you are ready.
                </p>
              </div>
            )}

            <div className={styles.finishCard}>
              <h3 className={styles.finishTitle}>Finish this episode</h3>
              <p className={styles.finishText}>
                When you are ready, save your progress and return to the
                dashboard.
              </p>

              <button onClick={markComplete} className={styles.continueButton}>
                Continue →
              </button>
            </div>
          </div>
        </div>
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
