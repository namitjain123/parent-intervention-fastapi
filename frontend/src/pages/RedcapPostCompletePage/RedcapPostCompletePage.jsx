import { useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from "../../config/config";

export default function RedcapPostCompletePage() {
  useEffect(() => {
    const run = async () => {
      try {
        const participantId =
          new URLSearchParams(window.location.search).get("participant_id") ||
          localStorage.getItem("participant_id");

        console.log("participantId in post redcap complete:", participantId);

        if (!participantId) {
          window.location.href = "/";
          return;
        }

        await axios.post(`${API_BASE_URL}/mark-postquestionnaire-complete`, {
          participant_id: participantId,
        });

        localStorage.removeItem("participant_id");
        window.location.href = "/";
      } catch (error) {
        console.error("Error completing post REDCap flow:", error);
      }
    };

    run();
  }, []);

  return <div style={{ padding: 40 }}>Finishing post-questionnaire...</div>;
}