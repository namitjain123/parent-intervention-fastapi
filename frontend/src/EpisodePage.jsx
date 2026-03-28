import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMsal } from "@azure/msal-react";
import axios from "axios";
import { apiRequest } from "./authConfig";

export default function EpisodePage() {
  const { episodeNumber } = useParams();
  const navigate = useNavigate();
  const { instance, accounts } = useMsal();

  const [episode, setEpisode] = useState(null);
  const [showTranscript, setShowTranscript] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);

  const startedAtRef = useRef(null);

  const getApiToken = async () => {
    const account = instance.getActiveAccount() || accounts[0];
    const response = await instance.acquireTokenSilent({
      ...apiRequest,
      account,
    });
    return response.accessToken;
  };

  const loadEpisode = async () => {
    try {
      const token = await getApiToken();

      const res = await axios.get(`http://127.0.0.1:8000/episodes/${episodeNumber}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      setEpisode(res.data);

      await axios.post(
        `http://127.0.0.1:8000/episodes/${episodeNumber}/start`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      startedAtRef.current = Date.now();
    } catch (err) {
      console.error(err);
    }
  };

  const markComplete = async () => {
    try {
      const token = await getApiToken();

      const startedAt = startedAtRef.current || Date.now();
      const timeSpentSeconds = Math.floor((Date.now() - startedAt) / 1000);

      await axios.post(
        `http://127.0.0.1:8000/episodes/${episodeNumber}/complete`,
        { time_spent_seconds: timeSpentSeconds },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      navigate("/");
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadEpisode();
  }, [episodeNumber]);

  const handleAnswerClick = (optionIndex) => {
    setSelectedAnswer(optionIndex);
    setShowExplanation(true);
  };

  const handleNextQuestion = () => {
    setSelectedAnswer(null);
    setShowExplanation(false);
    setCurrentQuestionIndex((prev) => prev + 1);
  };

  if (!episode) return <div style={{ padding: 40 }}>Loading episode...</div>;

  const currentQuestion = episode.quiz?.[currentQuestionIndex];
  const isLastQuestion = currentQuestionIndex === (episode.quiz?.length || 0) - 1;

  return (
    <div style={{ padding: 40, fontFamily: "Arial", maxWidth: "1100px", margin: "0 auto" }}>
      <h1>{episode.title}</h1>
      <p style={{ color: "#555", marginBottom: "20px" }}>{episode.description}</p>

      <div style={{ display: "flex", gap: "20px", alignItems: "flex-start" }}>
        {showTranscript && (
          <div
            style={{
              flex: 1,
              border: "1px solid #ddd",
              borderRadius: "12px",
              padding: "20px",
              backgroundColor: "#f9f9f9",
              maxHeight: "500px",
              overflowY: "auto",
              whiteSpace: "pre-wrap",
            }}
          >
            <h3>Transcript</h3>
            <p>{episode.transcript_text || "No transcript available."}</p>
          </div>
        )}

        <div style={{ flex: 2 }}>
          <div
            style={{
              border: "1px solid #ddd",
              borderRadius: "12px",
              padding: "20px",
              backgroundColor: "#fafafa",
              marginBottom: "20px",
            }}
          >
            <h3>Listen to this episode</h3>
            <audio controls style={{ width: "100%", marginTop: "10px" }}>
              <source src={episode.audio_url} type="audio/mpeg" />
              Your browser does not support the audio element.
            </audio>

            <button
              onClick={() => setShowTranscript(!showTranscript)}
              style={{ marginTop: "15px" }}
            >
              {showTranscript ? "Hide Transcript" : "Show Transcript"}
            </button>
          </div>

          {currentQuestion && (
            <div
              style={{
                border: "1px solid #ddd",
                borderRadius: "12px",
                padding: "20px",
                backgroundColor: "#fff",
                marginBottom: "20px",
              }}
            >
              <h3>
                Quiz Question {currentQuestionIndex + 1} of {episode.quiz.length}
              </h3>
              <p style={{ fontWeight: "bold" }}>{currentQuestion.question}</p>

              <div style={{ marginTop: "15px" }}>
                {currentQuestion.options.map((option, index) => (
                  <button
                    key={index}
                    onClick={() => handleAnswerClick(index)}
                    disabled={showExplanation}
                    style={{
                      display: "block",
                      width: "100%",
                      textAlign: "left",
                      padding: "12px",
                      marginBottom: "10px",
                      borderRadius: "8px",
                      border: "1px solid #ccc",
                      backgroundColor:
                        selectedAnswer === index ? "#e6f2ff" : "#fff",
                      cursor: showExplanation ? "default" : "pointer",
                    }}
                  >
                    {option}
                  </button>
                ))}
              </div>

              {showExplanation && (
                <div
                  style={{
                    marginTop: "20px",
                    padding: "15px",
                    borderRadius: "8px",
                    backgroundColor: "#f3f8f3",
                    border: "1px solid #cde5cd",
                  }}
                >
                  <p>
                    <strong>
                      {selectedAnswer === currentQuestion.correct_answer
                        ? "Correct!"
                        : "Incorrect."}
                    </strong>
                  </p>
                  <p>{currentQuestion.explanation}</p>

                  {!isLastQuestion ? (
                    <button onClick={handleNextQuestion} style={{ marginTop: "10px" }}>
                      Next
                    </button>
                  ) : (
                    <button onClick={markComplete} style={{ marginTop: "10px" }}>
                      Finish Episode
                    </button>
                  )}
                </div>
              )}
            </div>
          )}

          <button onClick={() => navigate("/")} style={{ marginRight: 10 }}>
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}