import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import axios from "axios";
import LoginPage from "./LoginPage";
import { apiRequest } from "./authConfig";
import { useState } from "react";

export default function App() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [message, setMessage] = useState("");

  const callBackend = async () => {
    try {
      const account = instance.getActiveAccount() || accounts[0];

      const response = await instance.acquireTokenSilent({
        ...apiRequest,
        account,
      });

      const token = response.accessToken;

      const res = await axios.get("http://127.0.0.1:8000/protected", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      setMessage(res.data.message);
    } catch (err) {
      console.error("Full error:", err);
      console.error("Response data:", err?.response?.data);
      console.error("Response status:", err?.response?.status);
      setMessage("Failed to call backend");
    }
  };

  const handleLogout = () => {
    instance.logoutRedirect();
  };

  if (!isAuthenticated) return <LoginPage />;

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h2>Dashboard</h2>
      <p>Welcome {accounts[0]?.name}</p>
      <button onClick={callBackend} style={{ marginRight: "10px" }}>
        Call Protected FastAPI
      </button>
      <button onClick={handleLogout}>Logout</button>
      <p>{message}</p>
    </div>
  );
}