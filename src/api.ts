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

export async function saveOnboarding(payload: {
  experience_level: string;
  learning_goal: string;
  preferred_language: string;
  daily_minutes: number;
  subjects: string[];
}) {
  const token = localStorage.getItem("learn2code_access_token");
  const response = await fetch(`${API_URL}/api/users/me/onboarding`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(payload),
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body?.detail ?? "Unable to save your onboarding preferences.");
  }
  return body;
}

export async function getSubjects() {
  const response = await fetch(`${API_URL}/api/subjects`);
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body?.detail ?? "Unable to load subjects from the Learn2Code API.");
  }
  return body as Array<{
    id: number;
    name: string;
    slug: string;
    category: string;
    description: string;
    difficulty: string;
    estimated_minutes: number;
  }>;
}
