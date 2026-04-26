import { useEffect } from "react";
import axios from "axios";

export default function RedcapCompletePage() {
  useEffect(() => {
    const run = async () => {
      try {
        const params = new URLSearchParams(window.location.search);

        const participantId =
          params.get("participant_id") || localStorage.getItem("participant_id");

        const userClass =
          params.get("user_class") || localStorage.getItem("user_class");

        console.log("participantId in redcap complete:", participantId);
        console.log("userClass in redcap complete:", userClass);

        if (!participantId || !userClass) {
          window.location.href = "/";
          return;
        }

        await axios.post("http://127.0.0.1:8000/mark-prequestionnaire-complete", {
          participant_id: participantId,
          user_class: userClass,
        });

        localStorage.removeItem("participant_id");
        localStorage.removeItem("user_class");

        window.location.href = "/";
      } catch (error) {
        console.error("Error completing REDCap flow:", error);
      }
    };

    run();
  }, []);

  return <div style={{ padding: 40 }}>Loading...</div>;
}