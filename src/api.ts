const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const ACCESS_TOKEN_KEY = "learn2code_access_token";
const REFRESH_TOKEN_KEY = "learn2code_refresh_token";

export type Profile = {
  experience_level: string | null;
  learning_goal: string | null;
  preferred_language: string | null;
  daily_minutes: number | null;
  subjects: string[];
  learning_hours: number;
  topics_completed: number;
  problems_solved: number;
  current_streak: number;
};

export type User = {
  id: number;
  full_name: string;
  email: string;
  role: string;
  profile: Profile | null;
};

type AuthResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
};

export type Dashboard = {
  learning_hours: number;
  topics_completed: number;
  problems_solved: number;
  current_streak: number;
  overall_progress: number;
  recommended_subjects: Array<{
    id: number;
    name: string;
    slug: string;
    category: string;
    description: string;
    difficulty: string;
    estimated_minutes: number;
    progress: number;
  }>;
  weekly_activity: number[];
  daily_goal_minutes: number;
  today_minutes: number;
};

function setTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
}

export function hasSession() {
  return Boolean(localStorage.getItem(ACCESS_TOKEN_KEY) && localStorage.getItem(REFRESH_TOKEN_KEY));
}

export function clearSession() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

async function parseResponse(response: Response) {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body?.detail ?? "Unable to connect to the Learn2Code API.");
  }
  return body;
}

export async function authenticate(
  mode: "login" | "signup",
  payload: { email: string; password: string; full_name?: string },
) {
  const response = await fetch(`${API_URL}/api/auth/${mode}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = (await parseResponse(response)) as AuthResponse;
  setTokens(body.access_token, body.refresh_token);
  return body;
}

export async function refreshSession() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) throw new Error("No refresh session is available.");
  const response = await fetch(`${API_URL}/api/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  const body = await parseResponse(response) as { access_token: string; refresh_token: string };
  setTokens(body.access_token, body.refresh_token);
  return body;
}

async function authorizedFetch(path: string, init?: RequestInit) {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  const headers = new Headers(init?.headers);
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  let response = await fetch(`${API_URL}${path}`, { ...init, headers });
  if (response.status === 401 && localStorage.getItem(REFRESH_TOKEN_KEY)) {
    await refreshSession();
    headers.set("Authorization", `Bearer ${localStorage.getItem(ACCESS_TOKEN_KEY)}`);
    response = await fetch(`${API_URL}${path}`, { ...init, headers });
  }
  return parseResponse(response);
}

export async function getCurrentUser() {
  return authorizedFetch("/api/auth/me") as Promise<User>;
}

export async function saveOnboarding(payload: {
  experience_level: string;
  learning_goal: string;
  preferred_language: string;
  daily_minutes: number;
  subjects: string[];
}) {
  return authorizedFetch("/api/users/me/onboarding", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }) as Promise<User>;
}

export async function getDashboard() {
  return authorizedFetch("/api/dashboard") as Promise<Dashboard>;
}

export async function recordActivity(minutes: number, activityType: "lesson" | "practice" | "quiz") {
  return authorizedFetch("/api/users/me/activity", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ minutes, activity_type: activityType }),
  }) as Promise<{ minutes: number; topics_completed: number }>;
}

export async function logout() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (refreshToken) {
    await fetch(`${API_URL}/api/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  }
  clearSession();
}

export async function getSubjects() {
  const response = await fetch(`${API_URL}/api/subjects`);
  const body = await parseResponse(response);
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
