import { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../../config/config";
import styles from "./DelayedRedcapCompletePage.module.css";

export default function DelayedRedcapCompletePage() {
  const [status, setStatus] = useState("loading"); // "loading" | "done" | "error"
  const [errorDetail, setErrorDetail] = useState("");

  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);

        const participantId =
          params.get("participant_id") || localStorage.getItem("participant_id");

        if (!participantId) {
          setStatus("error");
          setErrorDetail("No participant ID was found in the link.");
          return;
        }

        await axios.post(`${API_BASE_URL}/mark-delayed-survey-complete`, {
          participant_id: participantId,
        });

        localStorage.removeItem("participant_id");
        setStatus("done");
      } catch (error) {
        console.error("Error completing delayed REDCap flow:", error);
        setErrorDetail(error?.response?.data?.detail || "");
        setStatus("error");
      }
    };

    run();
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {status === "loading" && (
          <>
            <h1 className={styles.title}>Finishing up...</h1>
            <p className={styles.message}>Please wait while we save your responses.</p>
          </>
        )}

        {status === "done" && (
          <>
            <h1 className={styles.title}>Thank you!</h1>
            <p className={styles.message}>
              Your delayed survey has been recorded. Please return to the platform
              to continue with your episodes.
            </p>
            <a href="/" className={styles.returnButton}>Return to the platform</a>
          </>
        )}

        {status === "error" && (
          <>
            <h1 className={styles.title}>Something went wrong</h1>
            <p className={styles.error}>
              We couldn't record your delayed survey completion.
              {errorDetail ? ` (${errorDetail})` : ""} Please contact the research
              team for assistance.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
