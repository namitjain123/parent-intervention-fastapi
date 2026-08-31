import { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../../config/config";
import styles from "./RedcapPostCompletePage.module.css";

export default function RedcapPostCompletePage() {
  const [status, setStatus] = useState("loading"); // "loading" | "done" | "error"

  useEffect(() => {
    const run = async () => {
      try {
        const participantId =
          new URLSearchParams(window.location.search).get("participant_id") ||
          localStorage.getItem("participant_id");

        console.log("participantId in post redcap complete:", participantId);

        if (!participantId) {
          setStatus("error");
          return;
        }

        await axios.post(`${API_BASE_URL}/mark-postquestionnaire-complete`, {
          participant_id: participantId,
        });

        localStorage.removeItem("participant_id");
        setStatus("done");
      } catch (error) {
        console.error("Error completing post REDCap flow:", error);
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
              Thank you for completing the study. Your final survey has been recorded,
              and your participation is now complete. We appreciate the time you and
              your family gave to this research.
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <h1 className={styles.title}>Something went wrong</h1>
            <p className={styles.error}>
              We couldn't record your post-questionnaire completion. Please contact the
              research team for assistance.
            </p>
          </>
        )}
      </div>
    </div>
  );
}
