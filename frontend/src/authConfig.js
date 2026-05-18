export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_AZURE_CLIENT_ID,
    authority: import.meta.env.VITE_AZURE_AUTHORITY,
    knownAuthorities: [import.meta.env.VITE_AZURE_KNOWN_AUTHORITY],
    //redirectUri: import.meta.env.VITE_AZURE_REDIRECT_URI,
    //postLogoutRedirectUri: import.meta.env.VITE_AZURE_POST_LOGOUT_REDIRECT_URI,
    redirectUri: window.location.origin,
postLogoutRedirectUri: window.location.origin,
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
  system: {
    iframeHashTimeout: 15000,
    loadFrameTimeout: 15000,
  },
};

export const loginRequest = {
  scopes: ["openid", "profile", "email"],
};

export const apiRequest = {
  scopes: [import.meta.env.VITE_API_SCOPE],
};