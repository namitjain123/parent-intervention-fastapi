import { useEffect } from "react";
import axios from "axios";
import { API_BASE_URL } from "./config";

export default function RedcapCompletePage() {
  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);

        const participantId =
          params.get("participant_id") || localStorage.getItem("participant_id");

        const grade = params.get("grade");
        const teacher = params.get("teacher");

        console.log("participantId in redcap complete:", participantId);
        console.log("grade in redcap complete:", grade);
        console.log("teacher in redcap complete:", teacher);

        if (!participantId || !grade || !teacher) {
          window.location.href = "/";
          return;
        }

        await axios.post(`${API_BASE_URL}/mark-prequestionnaire-complete`, {
          participant_id: participantId,
          grade,
          teacher,
        });

        localStorage.removeItem("participant_id");

        window.location.href = "/";
      } catch (error) {
        console.error("Error completing REDCap flow:", error);
        const detail = error?.response?.data?.detail || error.message;
        alert(`Pre-questionnaire completion failed: ${detail}\n\nCheck the browser console for details.`);
        window.location.href = "/";
      }
    };

    run();
  }, []);

  return <div style={{ padding: 40 }}>Completing pre-questionnaire, please wait...</div>;
}