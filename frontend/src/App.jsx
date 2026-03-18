import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import axios from "axios";
import { apiRequest } from "./authConfig";
import LoginPage from "./LoginPage";
import { useEffect, useState } from "react";

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const [token, setToken] = useState("");
  const [dashboard, setDashboard] = useState(null);

  const getApiToken = async () => {
    const account = instance.getActiveAccount() || accounts[0];

    const response = await instance.acquireTokenSilent({
      ...apiRequest,
      account,
    });
    return response.accessToken;
  };

  const loadDashboard = async () => {
    try {
      const accessToken = await getApiToken();
      setToken(accessToken);

      await axios.get("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const res = await axios.get("http://127.0.0.1:8000/dashboard", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      setDashboard(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (isAuthenticated && accounts.length > 0) {
      loadDashboard();
    }
  }, [isAuthenticated, accounts]);

  const handleLogout = () => {
    instance.logoutRedirect();
  };

  const openPreQuestionnaire = async () => {
    try {
      const accessToken = token || await getApiToken();

      const meRes = await axios.get("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const participantId = meRes.data.azure_id;

      localStorage.setItem("participant_id", participantId);

      const redcapUrl = `${import.meta.env.VITE_REDCAP_PREQ_URL}&participant_id=${encodeURIComponent(participantId)}`;

      window.location.href = redcapUrl;
    } catch (err) {
      console.error(err);
    }
  };

  const completeEpisode = async (episodeNumber) => {
    try {
      const accessToken = token || await getApiToken();

      await axios.post(
        `http://127.0.0.1:8000/episodes/${episodeNumber}/complete`,
        {},
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );

      loadDashboard();
    } catch (err) {
      console.error(err);
    }
  };

  if (!isAuthenticated) return <LoginPage />;

  if (!dashboard) return <div style={{ padding: 40 }}>Loading dashboard...</div>;

  return (
    <div style={{ padding: 40, fontFamily: "Arial" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 20 }}>
        <h2>Parenting Platform</h2>
        <div>
          <span style={{ marginRight: 12 }}>{dashboard.name}</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </div>

      {!dashboard.pre_questionnaire_completed ? (
        <div>
          <h3>Pre-questionnaire required</h3>
          <p>Please complete the pre-questionnaire before accessing any episode.</p>
          <button onClick={openPreQuestionnaire}>Open Pre-questionnaire</button>
        </div>
      ) : (
        <div>
          <h3>Episodes</h3>
          {dashboard.episodes.map((ep) => (
            <div
              key={ep.episode_number}
              style={{
                border: "1px solid #ccc",
                borderRadius: 8,
                padding: 16,
                marginBottom: 12,
                background: ep.status === "locked" ? "#f3f3f3" : "white"
              }}
            >
              <h4>{ep.title}</h4>
              <p>Status: {ep.status}</p>
              {ep.status === "unlocked" && (
                <button onClick={() => completeEpisode(ep.episode_number)}>
                  Complete {ep.title}
                </button>
              )}
              {ep.status === "locked" && <button disabled>Locked</button>}
              {ep.status === "completed" && <button disabled>Completed</button>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}