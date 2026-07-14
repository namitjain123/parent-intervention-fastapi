import React from "react";
import ReactDOM from "react-dom/client";
import { PublicClientApplication, EventType } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage/DashboardPage";
import RedcapCompletePage from "./pages/RedcapCompletePage/RedcapCompletePage";
import { msalConfig } from "./config/authConfig";
import EpisodePage from "./pages/EpisodePage/EpisodePage";
import DelayedRedcapCompletePage from "./pages/DelayedRedcapCompletePage/DelayedRedcapCompletePage";
const msalInstance = new PublicClientApplication(msalConfig);

msalInstance.initialize().then(async () => {
  const response = await msalInstance.handleRedirectPromise();


  
  if (response && response.account) {
    msalInstance.setActiveAccount(response.account);
  } else {
    const accounts = msalInstance.getAllAccounts();
    if (accounts.length > 0) {
      msalInstance.setActiveAccount(accounts[0]);
    }
  }

  msalInstance.addEventCallback((event) => {
    if (event.eventType === EventType.LOGIN_SUCCESS && event.payload?.account) {
      msalInstance.setActiveAccount(event.payload.account);
    }
  });

  ReactDOM.createRoot(document.getElementById("root")).render(
    <React.StrictMode>
      <MsalProvider instance={msalInstance}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/redcap-complete" element={<RedcapCompletePage />} />
            <Route path="/delayed-redcap-complete" element={<DelayedRedcapCompletePage />} />
            <Route path="/episodes/:episodeNumber" element={<EpisodePage />} />
          </Routes>
        </BrowserRouter>
      </MsalProvider>
    </React.StrictMode>
  );
});