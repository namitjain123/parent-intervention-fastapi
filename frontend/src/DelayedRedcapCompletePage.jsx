import { useEffect } from "react";
import axios from "axios";

export default function DelayedRedcapCompletePage() {
  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);

        const participantId =
          params.get("participant_id") || localStorage.getItem("participant_id");

        if (!participantId) {
          window.location.href = "/";
          return;
        }

        await axios.post("http://127.0.0.1:8000/mark-delayed-survey-complete", {
          participant_id: participantId,
        });

        localStorage.removeItem("participant_id");
        window.location.href = "/";
      } catch (error) {
        console.error("Error completing delayed REDCap flow:", error);
      }
    };

    run();
  }, []);

  return <div style={{ padding: 40 }}>Finishing delayed survey...</div>;
}