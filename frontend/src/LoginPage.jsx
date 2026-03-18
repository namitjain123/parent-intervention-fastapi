import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { loginRequest } from "./authConfig";

export default function LoginPage() {
  const { instance } = useMsal();
  const isAuthenticated = useIsAuthenticated();

  const handleLogin = () => {
    instance.loginRedirect(loginRequest);
  };

  if (isAuthenticated) return null;

  return (
    <div style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Login / Signup Page</h1>
      <p>Please sign in or sign up using Azure.</p>
      <button onClick={handleLogin}>Sign In / Sign Up</button>
    </div>
  );
}