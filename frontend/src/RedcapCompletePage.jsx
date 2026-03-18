import { useEffect } from "react";
import axios from "axios";

export default function RedcapCompletePage() {
  useEffect(() => {
    const run = async () => {
      try {
        const participantId =
          new URLSearchParams(window.location.search).get("participant_id") ||
          localStorage.getItem("participant_id");

        console.log("participantId in redcap complete:", participantId);

        if (!participantId) {
          window.location.href = "/";
          return;
        }

        await axios.post("http://127.0.0.1:8000/mark-prequestionnaire-complete", {
          participant_id: participantId,
        });

        localStorage.removeItem("participant_id");
        window.location.href = "/";
      } catch (error) {
        console.error("Error completing REDCap flow:", error);
      }
    };

    run();
  }, []);

  return <div style={{ padding: 40 }}>Finishing questionnaire...</div>;
}