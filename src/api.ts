const API_URL = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");
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

export type Lesson = {
  id: number;
  subject_id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  code_example: string | null;
  video_url: string | null;
  order_index: number;
  estimated_minutes: number;
  completed: boolean;
};

export type PracticeProblem = {
  id: number;
  title: string;
  slug: string;
  description: string;
  difficulty: string;
  category: string;
  acceptance_rate: number;
  solved: boolean;
  topic?: string | null;
  pattern?: string | null;
  constraints?: string | null;
  examples?: Array<{ input: string; output: string }>;
  hints?: string[];
  editorial?: string | null;
  reference_url?: string | null;
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

export async function getLessons(subjectSlug: string) {
  return authorizedFetch(`/api/subjects/${encodeURIComponent(subjectSlug)}/lessons`) as Promise<Lesson[]>;
}

export async function completeLesson(lessonId: number) {
  return authorizedFetch(`/api/lessons/${lessonId}/complete`, { method: "POST" }) as Promise<Lesson>;
}

export async function getPracticeProblems() {
  return authorizedFetch("/api/practice/problems") as Promise<PracticeProblem[]>;
}

export async function submitPractice(problemId: number, language: string, code: string) {
  return authorizedFetch(`/api/practice/problems/${problemId}/submissions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ language, code }),
  }) as Promise<{ id: number; status: string; language: string }>;
}

export async function getPracticeProgress() {
  return authorizedFetch("/api/practice/progress") as Promise<Array<{
    problem_id: number;
    status: string;
    attempts: number;
    bookmarked: boolean;
    next_revision_at: string | null;
  }>>;
}

export async function updatePracticeProgress(problemId: number, status: "not_started" | "attempted" | "solved" | "revision", bookmarked?: boolean) {
  return authorizedFetch(`/api/practice/problems/${problemId}/progress`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, bookmarked }),
  });
}

export async function updateProfile(payload: { full_name: string; daily_minutes: number }) {
  return authorizedFetch("/api/users/me/profile", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }) as Promise<User>;
}

export async function getBookmarks() {
  return authorizedFetch("/api/users/me/bookmarks") as Promise<Array<{ id: number; target_type: string; target_id: number }>>;
}

export async function saveBookmark(targetType: "lesson" | "problem" | "subject", targetId: number) {
  return authorizedFetch("/api/users/me/bookmarks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ target_type: targetType, target_id: targetId }),
  });
}

export async function removeBookmark(targetType: string, targetId: number) {
  return authorizedFetch(`/api/users/me/bookmarks/${targetType}/${targetId}`, { method: "DELETE" });
}

export async function getHistory() {
  return authorizedFetch("/api/users/me/history") as Promise<Array<{ target_type: string; target_id: number; viewed_at: string }>>;
}

export type Recommendation = {
  id: number;
  title: string;
  reason: string;
  target_type: string;
  target_id: number;
  evidence: Record<string, number | string>;
};

export type Roadmap = {
  id: number;
  goal: string;
  experience_level: string;
  nodes: Array<{
    id: number;
    title: string;
    subject_id: number;
    lesson_id: number | null;
    node_type: string;
    order_index: number;
    estimated_minutes: number;
    prerequisite_ids: number[];
  }>;
};

export type Quiz = {
  id: number;
  title: string;
  difficulty: string;
  questions: Array<{ id: number; prompt: string; options: string[]; explanation: string }>;
};

export async function getRecommendations() {
  return authorizedFetch("/api/recommendations") as Promise<Recommendation[]>;
}

export async function getAnalytics() {
  return authorizedFetch("/api/analytics") as Promise<{
    measured: Record<string, number | Record<string, number>>;
    insights: string[];
  }>;
}

export async function createRoadmap(goal: string) {
  return authorizedFetch("/api/roadmaps", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal }),
  }) as Promise<Roadmap>;
}

export async function generateQuiz(payload: { subject_id?: number; difficulty?: string; question_count?: number }) {
  return authorizedFetch("/api/quizzes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  }) as Promise<Quiz>;
}

export async function submitQuiz(quizId: number, answers: Record<number, string>) {
  return authorizedFetch(`/api/quizzes/${quizId}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers: Object.fromEntries(Object.entries(answers).map(([id, answer]) => [String(id), answer])) }),
  }) as Promise<{ id: number; score: number; total: number }>;
}

export async function getRevisionQueue() {
  return authorizedFetch("/api/revision") as Promise<Array<{ id: number; topic: string; due_at: string; interval_days: number }>>;
}

export async function createRevision(topic: string) {
  return authorizedFetch(`/api/revision?topic=${encodeURIComponent(topic)}`, { method: "POST" });
}

export async function completeRevision(revisionId: number) {
  return authorizedFetch(`/api/revision/${revisionId}/complete`, { method: "POST" });
}

export type AIConversation = {
  id: number;
  title: string;
  teaching_mode: string;
  created_at: string;
  updated_at: string;
  messages: Array<{ id: number; role: string; content: string; created_at: string }>;
};

export async function createAIConversation(teachingMode = "beginner") {
  return authorizedFetch("/api/ai/conversations", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ teaching_mode: teachingMode }),
  }) as Promise<AIConversation>;
}

export async function getAIConversations() {
  return authorizedFetch("/api/ai/conversations") as Promise<AIConversation[]>;
}

export async function getAIConversation(id: number) {
  return authorizedFetch(`/api/ai/conversations/${id}`) as Promise<AIConversation>;
}

export async function sendAIMessage(id: number, content: string, context: Record<string, string>) {
  return authorizedFetch(`/api/ai/conversations/${id}/messages`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, context }),
  }) as Promise<{ id: number; role: string; content: string; created_at: string }>;
}
