const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function authenticate(
  mode: "login" | "signup",
  payload: { email: string; password: string; full_name?: string },
) {
  const response = await fetch(`${API_URL}/api/auth/${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body?.detail ?? "Unable to connect to the Learn2Code API.");
  }
  if (mode === "login") {
    localStorage.setItem("learn2code_access_token", body.access_token);
  }
  return body;
}
