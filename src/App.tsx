import { useEffect, useState, type FormEvent } from "react";
import { authenticate, clearSession, completeLesson as apiCompleteLesson, createAIConversation, getAIConversation, getAIConversations, getBookmarks, getCurrentUser, getDashboard, getHistory, getLessons, getPracticeProblems, getSubjects, hasSession, logout, recordActivity, runPractice, saveOnboarding, sendAIMessage, submitPractice, updateProfile, type AIConversation, type Dashboard, type Lesson, type PracticeProblem, type User } from "./api";

type Subject = {
  name: string;
  slug: string;
  category: string;
  description: string;
  progress: number;
  lessons: number;
  duration: string;
  color: string;
  icon: string;
};

const initialSubjects: Subject[] = [
  { name: "Python", slug: "python", category: "Programming", description: "Build a strong foundation with Python fundamentals and real projects.", progress: 0, lessons: 0, duration: "18h", color: "violet", icon: "Py" },
  { name: "Data Structures & Algorithms", slug: "data-structures-algorithms", category: "Computer science", description: "Master problem solving patterns that power great engineering interviews.", progress: 0, lessons: 0, duration: "32h", color: "cyan", icon: "DS" },
  { name: "React", slug: "react", category: "Web development", description: "Create fast, accessible interfaces with modern React and TypeScript.", progress: 0, lessons: 0, duration: "21h", color: "blue", icon: "Re" },
  { name: "SQL & Databases", slug: "sql-databases", category: "Backend", description: "Design reliable data models and write queries with confidence.", progress: 0, lessons: 0, duration: "14h", color: "orange", icon: "DB" },
];

const roadmap = [
  { title: "Python basics", subtitle: "Variables & syntax", state: "completed", x: 8, y: 22 },
  { title: "Control flow", subtitle: "Make decisions", state: "completed", x: 29, y: 11 },
  { title: "Data structures", subtitle: "Collections", state: "current", x: 51, y: 28 },
  { title: "Functions", subtitle: "Reusable logic", state: "available", x: 72, y: 13 },
  { title: "OOP", subtitle: "Build abstractions", state: "locked", x: 85, y: 38 },
  { title: "Final project", subtitle: "Ship something real", state: "locked", x: 62, y: 67 },
];

function Icon({ children }: { children: string }) {
  return <span className="icon" aria-hidden="true">{children}</span>;
}

function pageFromHash() {
  const page = window.location.hash.slice(1).toLowerCase();
  if (page === "explore" || page === "my-learning" || page === "practice" || page === "bookmarks" || page === "history" || page === "settings" || page === "ai-assistant") {
    return page === "my-learning" ? "My learning" : page === "ai-assistant" ? "AI Assistant" : page[0].toUpperCase() + page.slice(1);
  }
  return "Overview";
}

function AccountPage({ active, user, onUser }: { active: string; user: User | null; onUser: (user: User) => void }) {
  const [items, setItems] = useState<Array<{ target_type: string; target_id: number; viewed_at?: string }>>([]);
  const [name, setName] = useState(user?.full_name ?? "");
  const [minutes, setMinutes] = useState(user?.profile?.daily_minutes ?? 30);
  const [message, setMessage] = useState("");
  useEffect(() => {
    if (active === "Bookmarks") getBookmarks().then((rows) => setItems(rows.map((row) => ({ ...row })))).catch(() => setMessage("Bookmarks could not be loaded."));
    if (active === "History") getHistory().then(setItems).catch(() => setMessage("History could not be loaded."));
  }, [active]);
  async function saveSettings(event: FormEvent) {
    event.preventDefault();
    try {
      onUser(await updateProfile({ full_name: name, daily_minutes: minutes }));
      setMessage("Settings saved.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Settings could not be saved.");
    }
  }

  if (active === "Settings") return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">ACCOUNT</p><h1>Settings</h1><p className="muted">Keep your profile and daily goal up to date.</p></div></div><form className="onboarding-form" onSubmit={(event) => void saveSettings(event)}><label>Full name<input value={name} onChange={(event) => setName(event.target.value)} required /></label><label>Daily study time<select value={minutes} onChange={(event) => setMinutes(Number(event.target.value))}><option value={15}>15 minutes</option><option value={30}>30 minutes</option><option value={60}>1 hour</option><option value={90}>90 minutes</option></select></label>{message && <p className="auth-error" role="status">{message}</p>}<button className="primary-button" type="submit">Save settings <span>→</span></button></form></section>;
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">YOUR LIBRARY</p><h1>{active}</h1><p className="muted">{active === "Bookmarks" ? "Saved lessons and problems." : "Recently opened learning items."}</p></div></div>{message && <p className="auth-error" role="status">{message}</p>}<div className="problem-table">{items.length === 0 ? <p className="muted">Nothing here yet.</p> : items.map((item, index) => <div className="problem-row" key={`${item.target_type}-${item.target_id}-${index}`}><strong>{item.target_type} #{item.target_id}</strong><span className="muted">{item.viewed_at ? new Date(item.viewed_at).toLocaleString() : "Saved"}</span></div>)}</div></section>;
}

function AssistantPage({ user }: { user: User | null }) {
  const [conversations, setConversations] = useState<AIConversation[]>([]);
  const [conversation, setConversation] = useState<AIConversation | null>(null);
  const [message, setMessage] = useState("");
  const [mode, setMode] = useState("beginner");
  const [error, setError] = useState("");
  useEffect(() => { getAIConversations().then(setConversations).catch(() => setError("AI conversations could not be loaded.")); }, []);
  async function newConversation() {
    try { const created = await createAIConversation(mode); setConversation(created); setConversations((current) => [created, ...current]); setError(""); }
    catch (requestError) { setError(requestError instanceof Error ? requestError.message : "AI provider is unavailable."); }
  }
  async function send(event: FormEvent) {
    event.preventDefault();
    if (!conversation || !message.trim()) return;
    const text = message.trim(); setMessage("");
    try {
      const response = await sendAIMessage(conversation.id, text, { user_level: user?.profile?.experience_level ?? "beginner", learning_goal: user?.profile?.learning_goal ?? "programming" });
      setConversation((current) => current ? { ...current, messages: [...current.messages, { id: Date.now(), role: "user", content: text, created_at: new Date().toISOString() }, response] } : current);
    } catch (requestError) { setError(requestError instanceof Error ? requestError.message : "AI request failed."); }
  }
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">PERSONAL AI TUTOR</p><h1>Learn with your AI assistant</h1><p className="muted">Ask questions with your current learning context included.</p></div><div><select value={mode} onChange={(event) => setMode(event.target.value)}><option value="beginner">Beginner mode</option><option value="detailed">Detailed explanation</option><option value="interview">Interview preparation</option><option value="practical">Practical coding</option><option value="revision">Revision mode</option></select><button className="primary-button" onClick={() => void newConversation()}>New conversation</button></div></div><div className="ai-chat-layout"><aside className="problem-table">{conversations.map((item) => <button className="problem-row" key={item.id} onClick={() => getAIConversation(item.id).then(setConversation)}>{item.title}</button>)}</aside><div className="ai-chat-panel">{conversation ? <>{conversation.messages.map((item) => <div className={`chat-message ${item.role}`} key={item.id}><strong>{item.role === "assistant" ? "Learn2Code AI" : "You"}</strong><p>{item.content}</p></div>)}<form onSubmit={(event) => void send(event)}><input value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Ask your tutor..." /><button className="primary-button">Send</button></form></> : <p className="muted">Create a conversation to start learning.</p>}{error && <p className="auth-error" role="alert">{error}</p>}</div></div></section>;
}

function WorkspacePage({ active, subjects, onSelect, dashboard, practiceProblems }: { active: string; subjects: Subject[]; onSelect: (subject: Subject) => void; dashboard: Dashboard | null; practiceProblems: PracticeProblem[] }) {
  const [selectedProblem, setSelectedProblem] = useState<PracticeProblem | null>(null);
  const [code, setCode] = useState("");
  const [language, setLanguage] = useState("python");
  const [problemTab, setProblemTab] = useState<"problem" | "hints" | "editorial">("problem");
  const [difficultyFilter, setDifficultyFilter] = useState("all");
  const [topicFilter, setTopicFilter] = useState("all");
  const [testInput, setTestInput] = useState("");
  const [runOutput, setRunOutput] = useState("");
  const [submissionMessage, setSubmissionMessage] = useState("");
  const visibleProblems = practiceProblems.filter((problem) =>
    (difficultyFilter === "all" || problem.difficulty.toLowerCase() === difficultyFilter)
    && (topicFilter === "all" || problem.topic === topicFilter),
  );
  async function submitSelectedProblem() {
    if (!selectedProblem || !code.trim()) return;
    try {
      await submitPractice(selectedProblem.id, language, code);
      setSubmissionMessage("Submitted successfully.");
      setRunOutput("Accepted — submission recorded.");
    } catch (error) {
      setSubmissionMessage(error instanceof Error ? error.message : "Submission failed.");
    }
  }
  async function runSelectedProblem() {
    if (!selectedProblem || !code.trim()) {
      setRunOutput("Write code before running.");
      return;
    }
    try {
      const result = await runPractice(selectedProblem.id, language, code, testInput);
      setRunOutput(`${result.status.toUpperCase()} (${result.duration_ms}ms)\n${result.stdout || result.stderr || "No output."}`);
    } catch (error) {
      setRunOutput(error instanceof Error ? error.message : "Code execution failed.");
    }
  }
  if (active === "Explore") {
    return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">LEARNING LIBRARY</p><h1>Explore your next skill</h1><p className="muted">Structured paths built to take you from curious to capable.</p></div><button className="filter-button">All categories <span>⌄</span></button></div><div className="explore-hero"><div><span className="hero-label">CURATED FOR YOU</span><h2>Build skills that<br /><em>compound.</em></h2><p>Choose a path, show up consistently, and let your progress do the talking.</p></div><div className="path-orbit">✦</div></div><div className="section-heading"><div><h3>All subjects</h3><p className="muted">{subjects.length} learning paths available</p></div></div><div className="explore-grid">{subjects.map((subject) => <button className="explore-card" key={subject.name} onClick={() => onSelect(subject)}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><span className="tag">{subject.category}</span><h3>{subject.name}</h3><p>{subject.description}</p><div className="explore-meta"><span>{subject.lessons} lessons</span><span>{subject.duration}</span><b>View path →</b></div></button>)}</div></section>;
  }
  if (active === "Practice") {
    return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">CODING PRACTICE</p><h1>Sharpen your problem solving</h1><p className="muted">Practice deliberately. Build confidence one problem at a time.</p></div></div><div className="practice-stats"><div><strong>{dashboard?.problems_solved ?? 0}</strong><span>Problems solved</span></div><div><strong>{visibleProblems.length ? `${Math.round(visibleProblems.reduce((sum, problem) => sum + problem.acceptance_rate, 0) / visibleProblems.length)}%` : "—"}</strong><span>Acceptance rate</span></div><div><strong>{dashboard?.current_streak ?? 0}</strong><span>Day streak</span></div><div><strong>{dashboard?.problems_solved ? language : "—"}</strong><span>Languages used</span></div></div><div className="section-heading"><div><h3>Problem set</h3><p className="muted">{visibleProblems.length} problems in this view</p></div><div className="practice-filters"><select value={difficultyFilter} onChange={(event) => setDifficultyFilter(event.target.value)}><option value="all">All levels</option><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select><select value={topicFilter} onChange={(event) => setTopicFilter(event.target.value)}><option value="all">All topics</option>{Array.from(new Set(practiceProblems.map((problem) => problem.topic).filter(Boolean))).map((topic) => <option value={topic ?? ""} key={topic}>{topic}</option>)}</select></div></div><div className="problem-table"><div className="problem-header"><span>PROBLEM</span><span>DIFFICULTY</span><span>CATEGORY</span><span>ACCEPTANCE</span><span /></div>{visibleProblems.map((problem) => <button className="problem-row" key={problem.id} onClick={() => {     setSelectedProblem(problem); setCode(problem.starter_code ?? ""); setLanguage("python"); setProblemTab("problem"); setTestInput(""); setRunOutput(""); setSubmissionMessage(""); }}><span><i className={problem.solved ? "solved" : "○"}>{problem.solved ? "✓" : "○"}</i><strong>{problem.title}</strong></span><span className={`problem-difficulty ${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span><span className="muted">{problem.category}</span><span className="muted">{problem.acceptance_rate || "—"}%</span><b>→</b></button>)}</div>{selectedProblem && <div className="lesson-backdrop" onClick={() => setSelectedProblem(null)}><section className="leetcode-modal" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><p className="eyebrow">DSA PROBLEM WORKSPACE</p><h2>{selectedProblem.title}</h2><p className="muted">{selectedProblem.topic ?? selectedProblem.category} · {selectedProblem.pattern ?? "Practice pattern"} · {selectedProblem.difficulty}</p></div><button className="close-button" onClick={() => setSelectedProblem(null)}>×</button></div><div className="problem-tabs"><button className={problemTab === "problem" ? "active" : ""} onClick={() => setProblemTab("problem")}>Description</button><button className={problemTab === "hints" ? "active" : ""} onClick={() => setProblemTab("hints")}>Hints</button><button className={problemTab === "editorial" ? "active" : ""} onClick={() => setProblemTab("editorial")}>Editorial</button></div><div className="leetcode-grid"><article className="problem-pane">{problemTab === "problem" && <div className="problem-learning-content"><p>{selectedProblem.description}</p>{selectedProblem.constraints && <><h3>Constraints</h3><p>{selectedProblem.constraints}</p></>}{selectedProblem.examples?.map((example, index) => <div className="example-block" key={example.input}><strong>Example {index + 1}</strong><pre><code>Input: {example.input}{"\n"}Output: {example.output}</code></pre></div>)}</div>}{problemTab === "hints" && <ol className="problem-learning-content">{(selectedProblem.hints ?? []).map((hint) => <li key={hint}>{hint}</li>)}</ol>}{problemTab === "editorial" && <div className="problem-learning-content"><p>{selectedProblem.editorial ?? "Editorial will be added for this problem."}</p>{selectedProblem.reference_url && <a href={selectedProblem.reference_url} target="_blank" rel="noreferrer">Open public reference ↗</a>}</div>}</article><article className="editor-pane"><div className="editor-toolbar"><span>Code</span><select value={language} onChange={(event) => setLanguage(event.target.value)}><option value="python">Python</option><option value="javascript">JavaScript</option><option value="typescript">TypeScript</option><option value="java">Java</option><option value="c">C</option><option value="cpp">C++</option><option value="csharp">C#</option></select></div>    <textarea className="leetcode-editor" value={code} onChange={(event) => setCode(event.target.value)} spellCheck={false} placeholder={`Write your ${language} solution here...`} /><div className="testcase-panel"><strong>Testcase input</strong><textarea value={testInput} onChange={(event) => setTestInput(event.target.value)} placeholder="Example: 2 7 11 15\n9" rows={3} /><div className="editor-actions"><button className="secondary-button" onClick={() => void runSelectedProblem()}>Run Code</button><button className="primary-button" onClick={() => void submitSelectedProblem()}>Submit</button></div>{runOutput && <p className="editor-result" role="status">{runOutput}</p>}{submissionMessage && <p className="editor-result" role="status">{submissionMessage}</p>}</div></article></div></section></div>}</section>;
  }
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">YOUR PROGRESS</p><h1>My learning</h1><p className="muted">A clear view of everything you&apos;re building.</p></div><button className="secondary-button">Edit daily goal</button></div><div className="learning-overview"><div className="overview-ring"><strong>{dashboard?.overall_progress ?? 0}%</strong><span>overall progress</span></div><div><h3>You&apos;re building a habit.</h3><p className="muted">You&apos;ve learned for {dashboard?.learning_hours ?? 0} hours across {subjects.length} active paths. Keep your streak alive today.</p><div className="progress-track"><div style={{ width: `${dashboard?.overall_progress ?? 0}%` }} /></div><small>{dashboard?.topics_completed ?? 0} topics completed</small></div></div><div className="section-heading"><div><h3>Active learning paths</h3><p className="muted">Continue where you left off</p></div></div><div className="my-learning-list">{subjects.map((subject) => <button className="my-learning-row" key={subject.name} onClick={() => onSelect(subject)}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><div><strong>{subject.name}</strong><span>{subject.progress}% complete · {subject.lessons} lessons</span></div><div className="progress-track"><div style={{ width: `${subject.progress}%` }} /></div><b>→</b></button>)}</div></section>;
}

function LessonView({ subject, lesson, onClose, onComplete }: { subject: Subject; lesson?: Lesson; onClose: () => void; onComplete: () => void }) {
  const [completed, setCompleted] = useState(lesson?.completed ?? false);
  const [error, setError] = useState("");
  async function completeLesson() {
    if (completed) return;
    try {
      if (lesson) await apiCompleteLesson(lesson.id);
      else await recordActivity(45, "lesson");
      setCompleted(true);
      onComplete();
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save lesson progress.");
    }
  }

  return <div className="lesson-backdrop"><section className="lesson-modal"><header className="lesson-header"><div><button className="back-button" onClick={onClose}>← Back to roadmap</button><p className="eyebrow">LESSON {lesson?.order_index ?? 1}</p><h1>{lesson?.title ?? "Working with collections"}</h1><p className="muted">{subject.name} · {lesson?.estimated_minutes ?? 45} minutes</p></div><button className="close-button" onClick={onClose}>×</button></header><div className="lesson-progress"><span style={{ width: completed ? "100%" : "68%" }} /></div><div className="lesson-layout"><article className="lesson-content"><div className="video-placeholder"><div className="play-button">▶</div><span>{lesson?.summary ?? "Introduction to collections"}</span><small>{lesson?.video_url ? "Video lesson" : "Reading lesson"}</small></div><h2>{lesson?.title ?? "Make your data work for you"}</h2><p>{lesson?.content ?? "Collections let you group and organize related values."}</p>{lesson?.code_example && <pre><code>{lesson.code_example}</code></pre>}{error && <p className="auth-error" role="alert">{error}</p>}<button className={`complete-button ${completed ? "done" : ""}`} onClick={() => void completeLesson()}>{completed ? "✓ Lesson completed" : "Mark lesson as complete"} <span>{completed ? "" : "→"}</span></button></article></div></section></div>;
}

function AuthDialog({ onClose, onAuthenticated }: { onClose: () => void; onAuthenticated: (user: User) => void }) {
  const [mode, setMode] = useState<"login" | "signup">("login");
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [onboarding, setOnboarding] = useState(false);
  const [experience, setExperience] = useState("beginner");
  const [goal, setGoal] = useState("Become a Full-Stack Developer");
  const [language, setLanguage] = useState("Python");
  const [minutes, setMinutes] = useState(30);
  const [selectedSubjects, setSelectedSubjects] = useState(["Python", "Data Structures & Algorithms"]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const response = await authenticate(mode, { full_name: fullName, email, password });
      if (mode === "signup") setOnboarding(true);
      else {
        onAuthenticated(response.user);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Authentication failed.");
    }
  }

  async function finishOnboarding(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const user = await saveOnboarding({ experience_level: experience, learning_goal: goal, preferred_language: language, daily_minutes: minutes, subjects: selectedSubjects });
      onAuthenticated(user);
      setOnboarding(false);
      setSubmitted(true);
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to save onboarding.");
    }
  }

  function toggleSubject(subject: string) {
    setSelectedSubjects((current) => current.includes(subject) ? current.filter((item) => item !== subject) : [...current, subject]);
  }

  return <div className="auth-backdrop" onClick={onClose}><section className="auth-dialog" onClick={(event) => event.stopPropagation()}><button className="close-button auth-close" onClick={onClose}>×</button><div className="auth-brand"><span className="brand-mark">&lt;/&gt;</span><strong>learn<span>2</span>code</strong></div>{onboarding ? <form className="onboarding-form" onSubmit={finishOnboarding}><p className="eyebrow">PERSONALIZE YOUR PATH</p><h2>Make learning fit you.</h2><p className="muted">A few answers help us shape your first recommendations.</p><label>Experience level<select value={experience} onChange={(event) => setExperience(event.target.value)}><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label><label>Your main goal<select value={goal} onChange={(event) => setGoal(event.target.value)}><option>Become a Full-Stack Developer</option><option>Master DSA</option><option>Learn Programming</option><option>Explore Computer Science</option></select></label><label>Preferred language<select value={language} onChange={(event) => setLanguage(event.target.value)}><option>Python</option><option>JavaScript</option><option>TypeScript</option><option>Java</option><option>C++</option></select></label><label>Daily study time<select value={minutes} onChange={(event) => setMinutes(Number(event.target.value))}><option value={15}>15 minutes</option><option value={30}>30 minutes</option><option value={60}>1 hour</option><option value={90}>90 minutes</option></select></label><div><span className="form-label">What do you want to learn?</span><div className="subject-pills">{["Python", "Data Structures & Algorithms", "React", "SQL & Databases"].map((subject) => <button type="button" className={selectedSubjects.includes(subject) ? "subject-pill selected" : "subject-pill"} onClick={() => toggleSubject(subject)} key={subject}>{selectedSubjects.includes(subject) ? "✓ " : ""}{subject}</button>)}</div></div>{error && <p className="auth-error" role="alert">{error}</p>}<button className="primary-button auth-submit" type="submit">Build my learning path <span>→</span></button></form> : submitted ? <div className="auth-success"><div>✓</div><h2>{mode === "signup" ? "You&apos;re all set" : "Welcome back"}</h2><p className="muted">{mode === "signup" ? "Your personalized learning path is ready." : "You are signed in to your Learn2Code account."}</p><button className="primary-button" onClick={onClose}>Continue learning <span>→</span></button></div> : <><p className="eyebrow">{mode === "login" ? "WELCOME BACK" : "GET STARTED"}</p><h2>{mode === "login" ? "Sign in to your workspace" : "Create your account"}</h2><p className="muted">{mode === "login" ? "Continue building your skills." : "Start your personalized learning journey."}</p><form onSubmit={submit}>{mode === "signup" && <label>Full name<input required value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Yogesh Chavan" /></label>}<label>Email address<input required type="email" value={email} onChange={(event) => setEmail(event.target.value)} placeholder="you@example.com" /></label><label>Password<input required minLength={8} type="password" value={password} onChange={(event) => setPassword(event.target.value)} placeholder="At least 8 characters" /></label>{error && <p className="auth-error" role="alert">{error}</p>}<button className="primary-button auth-submit" type="submit">{mode === "login" ? "Sign in" : "Create account"} <span>→</span></button></form><button className="auth-switch" onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); }}>{mode === "login" ? "New to Learn2Code? Create an account" : "Already have an account? Sign in"}</button></>}</section></div>;
}

export function App() {
  const [active, setActive] = useState(pageFromHash);
  const [subjects, setSubjects] = useState(initialSubjects);
  const [selectedSubject, setSelectedSubject] = useState(initialSubjects[0]);
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<Lesson | undefined>();
  const [search, setSearch] = useState("");
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [roadmapTab, setRoadmapTab] = useState<"roadmap" | "syllabus" | "notes" | "videos">("roadmap");
  const [showLesson, setShowLesson] = useState(false);
  const [showAuth, setShowAuth] = useState(!hasSession());
  const [user, setUser] = useState<User | null>(null);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [practiceProblems, setPracticeProblems] = useState<PracticeProblem[]>([]);
  const [apiError, setApiError] = useState("");
  const closeAuth = () => {
    if (user) setShowAuth(false);
  };
  function navigate(page: string) {
    setActive(page);
    window.history.pushState({}, "", `#${page === "My learning" ? "my-learning" : page === "AI Assistant" ? "ai-assistant" : page.toLowerCase()}`);
  }
  useEffect(() => {
    if (user && selectedSubject.slug) {
      getLessons(selectedSubject.slug).then(setLessons).catch(() => setLessons([]));
    }
  }, [selectedSubject, user]);
  useEffect(() => {
    const handleNavigation = () => setActive(pageFromHash());
    window.addEventListener("popstate", handleNavigation);
    window.addEventListener("hashchange", handleNavigation);
    return () => {
      window.removeEventListener("popstate", handleNavigation);
      window.removeEventListener("hashchange", handleNavigation);
    };
  }, []);
  useEffect(() => {
    if (hasSession()) {
      Promise.all([getCurrentUser(), getDashboard()]).then(([currentUser, currentDashboard]) => {
        setUser(currentUser);
        setDashboard(currentDashboard);
        setShowAuth(false);
      }).catch(() => {
        clearSession();
        setShowAuth(true);
      });
    }
    getSubjects().then((remoteSubjects) => {
      if (remoteSubjects.length === 0) return;
      const mappedSubjects = remoteSubjects.map((subject, index) => ({
        name: subject.name,
        slug: subject.slug,
        category: subject.category,
        description: subject.description,
        progress: initialSubjects[index % initialSubjects.length]?.progress ?? 0,
        lessons: Math.max(1, Math.round(subject.estimated_minutes / 25)),
        duration: `${Math.max(1, Math.round(subject.estimated_minutes / 60))}h`,
        color: initialSubjects[index % initialSubjects.length]?.color ?? "violet",
        icon: subject.name.slice(0, 2),
      }));
      setSubjects(mappedSubjects);
      setSelectedSubject(mappedSubjects[0]);
      setApiError("");
    }).catch((error: unknown) => {
      setApiError(error instanceof Error ? error.message : "The subject API is unavailable.");
    });
    if (hasSession()) {
      getPracticeProblems().then(setPracticeProblems).catch(() => setApiError("Practice problems could not be loaded."));
    }
  }, []);
  useEffect(() => {
    if (!dashboard) return;
    const progressByName = new Map(dashboard.recommended_subjects.map((subject) => [subject.name, subject.progress]));
    setSubjects((current) => current.map((subject) => (
      progressByName.has(subject.name) ? { ...subject, progress: progressByName.get(subject.name) ?? 0 } : subject
    )));
  }, [dashboard]);
  const filteredSubjects = subjects.filter((subject) =>
    `${subject.name} ${subject.category}`.toLowerCase().includes(search.toLowerCase()),
  );

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">&lt;/&gt;</span><span>learn<span>2</span>code</span></div>
        <div className="workspace-label">WORKSPACE</div>
        <nav className="nav-list" aria-label="Main navigation">
          {["Overview", "Explore", "My learning", "Practice"].map((item, index) => (
            <button className={active === item ? "nav-item active" : "nav-item"} onClick={() => navigate(item)} key={item}>
              <Icon>{["⌂", "◈", "▣", "⌘"][index]}</Icon>{item}
              {item === "My learning" && <span className="nav-count">4</span>}
            </button>
          ))}
          <button className={active === "AI Assistant" ? "nav-item active" : "nav-item"} onClick={() => navigate("AI Assistant")}><Icon>✦</Icon>AI Assistant</button>
        </nav>
        <div className="workspace-label library-label">YOUR LIBRARY</div>
        <nav className="nav-list">
          <button className={active === "Bookmarks" ? "nav-item active" : "nav-item"} onClick={() => navigate("Bookmarks")}><Icon>☆</Icon>Bookmarks</button>
          <button className={active === "History" ? "nav-item active" : "nav-item"} onClick={() => navigate("History")}><Icon>◷</Icon>History</button>
        </nav>
        <div className="sidebar-bottom">
          <div className="upgrade-card"><span className="sparkle">✦</span><strong>Unlock your potential</strong><p>Get unlimited access to every learning path.</p><button>Explore Pro <span>→</span></button></div>
          <button className={active === "Settings" ? "nav-item active" : "nav-item"} onClick={() => navigate("Settings")}><Icon>⚙</Icon>Settings</button>
          <button className="profile-mini" onClick={async () => { await logout(); setUser(null); setDashboard(null); setShowAuth(true); }}><div className="avatar">{user?.full_name.slice(0, 2).toUpperCase() ?? "YC"}</div><div><strong>{user?.full_name ?? "Learner"}</strong><small>Free plan · Sign out</small></div><span className="more">•••</span></button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><b>/</b>{active}</div>
          <div className="top-actions"><label className="search"><span>⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search anything..." /><kbd>⌘ K</kbd></label><button className="icon-button">◔</button><button className="icon-button notification">♢<i /></button></div>
        </header>

        <div className={`content ${active === "Overview" ? "" : "alternate"}`}>
          {apiError && <div className="api-notice" role="status"><span>!</span><p><strong>Using local subject data</strong>{apiError}</p><button onClick={() => setApiError("")}>×</button></div>}
          {active === "AI Assistant" ? <AssistantPage user={user} /> : ["Bookmarks", "History", "Settings"].includes(active) ? <AccountPage active={active} user={user} onUser={setUser} /> : <WorkspacePage active={active} subjects={filteredSubjects} dashboard={dashboard} practiceProblems={practiceProblems} onSelect={(subject) => { setSelectedSubject(subject); setShowRoadmap(true); }} />}
          <section className="welcome-row">
            <div><p className="eyebrow">FRIDAY, NOVEMBER 14, 2026</p><h1>Good morning, {user?.full_name.split(" ")[0] ?? "Learner"} <span>✦</span></h1><p className="muted">Small steps every day lead to big results. Let&apos;s keep building.</p></div>
            <button className="streak"><span>♨</span><strong>12 day streak</strong><small>Keep it going!</small></button>
          </section>

          <section className="hero-card">
            <div className="hero-copy"><div className="hero-label"><span className="pulse-dot" /> CONTINUE LEARNING</div><h2>Python for<br /><em>problem solvers.</em></h2><p>Pick up where you left off. You&apos;re making great progress.</p><div className="hero-progress"><span><b>68%</b> complete</span><span>28 / 42 lessons</span></div><div className="progress-track"><div style={{ width: "68%" }} /></div><button className="primary-button" onClick={() => setShowRoadmap(true)}>Continue lesson <span>→</span></button></div>
            <div className="hero-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="code-card"><span>def</span> <b>solve</b>(problem):<br /><i>    while</i> not solved:<br /><span>        learn()</span><br />    return <b>growth</b></div><div className="floating-badge badge-one">✦  +1 XP</div><div className="floating-badge badge-two">✓  3 day goal</div></div>
          </section>

          <section className="stats-grid">
            <div className="stat-card"><div className="stat-icon violet-bg">◒</div><div><span>Learning hours</span><strong>{dashboard?.learning_hours ?? 0} <small>hrs</small></strong><p className="positive">Live from your profile</p></div></div>
            <div className="stat-card"><div className="stat-icon cyan-bg">✓</div><div><span>Topics completed</span><strong>{dashboard?.topics_completed ?? 0} <small>/ 64</small></strong><p className="positive">Live from your profile</p></div></div>
            <div className="stat-card"><div className="stat-icon orange-bg">⌘</div><div><span>Problems solved</span><strong>{dashboard?.problems_solved ?? 0}</strong><p className="positive">Live from your profile</p></div></div>
            <div className="stat-card"><div className="stat-icon pink-bg">♨</div><div><span>Current streak</span><strong>{dashboard?.current_streak ?? 0} <small>days</small></strong><p className="muted">From your activity</p></div></div>
          </section>

          <div className="section-heading"><div><h3>Pick up where you left off</h3><p className="muted">Your active learning paths</p></div><button className="text-button">View all <span>→</span></button></div>
          <section className="learning-grid">
            {subjects.slice(0, 3).map((subject) => <button className="learning-card" key={subject.name} onClick={() => { setSelectedSubject(subject); setShowRoadmap(true); }}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><div className="card-top"><span className="tag">{subject.category}</span><span className="bookmark">☆</span></div><h4>{subject.name}</h4><p>{subject.progress === 68 ? "Functions & modules" : subject.progress === 34 ? "Trees & graphs" : "Components & props"}</p><div className="card-progress"><div className="progress-track"><div style={{ width: `${subject.progress}%` }} /></div><span>{subject.progress}%</span></div><div className="card-footer"><span>{subject.lessons} lessons</span><span>→</span></div></button>)}
          </section>

          <div className="section-heading explore-heading"><div><h3>Explore subjects</h3><p className="muted">Find your next thing to learn</p></div><button className="filter-button">All subjects <span>⌄</span></button></div>
          <section className="subject-grid">{filteredSubjects.map((subject) => <button className="subject-row" key={subject.name} onClick={() => { setSelectedSubject(subject); setShowRoadmap(true); }}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><div className="subject-info"><strong>{subject.name}</strong><span>{subject.category} · {subject.lessons} lessons</span></div><div className="difficulty"><span className={`difficulty-dot ${subject.progress > 50 ? "green" : ""}`} />{subject.progress > 50 ? "Intermediate" : "Beginner"}</div><span className="subject-time">{subject.duration}</span><span className="arrow">→</span></button>)}</section>

          <div className="lower-grid"><section className="activity-panel"><div className="section-heading"><div><h3>Weekly activity</h3><p className="muted">Your learning rhythm</p></div><span className="week-label">This week ⌄</span></div><div className="chart"><div className="chart-y"><span>4h</span><span>3h</span><span>2h</span><span>1h</span><span>0</span></div><div className="chart-area">{(dashboard?.weekly_activity ?? [0, 0, 0, 0, 0, 0, 0]).map((minutes, index, activity) => <div className="bar-column" key={index}><div className={`bar ${index === activity.length - 1 ? "today" : ""}`} style={{ height: `${Math.min(100, minutes / 2)}%` }} /><span>{["M", "T", "W", "T", "F", "S", "S"][index]}</span></div>)}</div></div></section><section className="goals-panel"><div className="section-heading"><div><h3>Today&apos;s goal</h3><p className="muted">Friday, November 14</p></div><span className="goal-percent">{dashboard ? Math.min(100, Math.round((dashboard.today_minutes / dashboard.daily_goal_minutes) * 100)) : 0}%</span></div><div className="goal-ring"><div><strong>{dashboard ? Math.max(0, dashboard.daily_goal_minutes - dashboard.today_minutes) : 0}</strong><span>min left</span></div></div><p className="goal-message">{dashboard?.today_minutes ? "You&apos;re making progress. Keep going." : "Start a lesson to begin today&apos;s goal."}</p><button className="secondary-button" onClick={() => setShowRoadmap(true)}>View your plan <span>→</span></button></section></div>
        </div>
      </main>

      {showRoadmap && <div className="modal-backdrop" onClick={() => setShowRoadmap(false)}><section className="roadmap-modal" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><span className="eyebrow">SUBJECT WORKSPACE</span><h2>{selectedSubject.name}</h2><p className="muted">Roadmap, syllabus, notes, and video slots in one place.</p></div><button className="close-button" onClick={() => setShowRoadmap(false)}>×</button></div><div className="roadmap-toolbar"><button className={roadmapTab === "roadmap" ? "active" : ""} onClick={() => setRoadmapTab("roadmap")}>Roadmap</button><button className={roadmapTab === "syllabus" ? "active" : ""} onClick={() => setRoadmapTab("syllabus")}>Syllabus</button><button className={roadmapTab === "notes" ? "active" : ""} onClick={() => setRoadmapTab("notes")}>Notes</button><button className={roadmapTab === "videos" ? "active" : ""} onClick={() => setRoadmapTab("videos")}>Videos</button></div>{roadmapTab === "roadmap" && <><div className="roadmap-canvas">{lessons.length ? lessons.map((lesson, index) => <button className={`roadmap-node ${lesson.completed ? "completed" : index === 0 ? "current" : "available"}`} style={{ left: `${15 + (index % 4) * 23}%`, top: `${25 + Math.floor(index / 4) * 35}%` }} key={lesson.id} onClick={() => { setSelectedLesson(lesson); setShowRoadmap(false); setShowLesson(true); }}><span>{lesson.completed ? "✓" : "→"}</span><strong>{lesson.title}</strong><small>{lesson.estimated_minutes} min</small></button>) : roadmap.map((node) => <button className={`roadmap-node ${node.state}`} style={{ left: `${node.x}%`, top: `${node.y}%` }} key={node.title}><span>→</span><strong>{node.title}</strong><small>{node.subtitle}</small></button>)}</div><div className="roadmap-footer"><div><strong>{lessons[0]?.title ?? "Start your learning path"}</strong><span>Estimated time · {lessons[0]?.estimated_minutes ?? 45} min</span></div><button className="primary-button" onClick={() => { setSelectedLesson(lessons[0]); setShowRoadmap(false); setShowLesson(true); }}>Start learning <span>→</span></button></div></>}{roadmapTab === "syllabus" && <div className="subject-resource-list">{lessons.map((lesson) => <button className="problem-row" key={lesson.id} onClick={() => { setSelectedLesson(lesson); setShowRoadmap(false); setShowLesson(true); }}><strong>{lesson.order_index}. {lesson.title}</strong><span>{lesson.estimated_minutes} min · {lesson.completed ? "Completed" : "Not started"}</span></button>)}</div>}{roadmapTab === "notes" && <div className="subject-resource-list">{lessons.map((lesson) => <article className="subject-note" key={lesson.id}><h3>{lesson.title}</h3><p>{lesson.content}</p>{lesson.code_example && <pre><code>{lesson.code_example}</code></pre>}</article>)}</div>}{roadmapTab === "videos" && <div className="subject-video-placeholder"><strong>Video lessons will appear here</strong><p>Video slots are ready. Add your trusted course links later without changing the subject structure.</p></div>}</section></div>}
      {showLesson && <LessonView subject={selectedSubject} lesson={selectedLesson} onClose={() => setShowLesson(false)} onComplete={() => { getDashboard().then(setDashboard).catch(() => setApiError("Dashboard data could not be refreshed.")); getLessons(selectedSubject.slug).then(setLessons).catch(() => undefined); }} />}
      {user && active !== "AI Assistant" && <button className="ai-floating-button" onClick={() => navigate("AI Assistant")} aria-label="Open AI assistant">✦</button>}
      {showAuth && <AuthDialog onClose={closeAuth} onAuthenticated={(authenticatedUser) => { setUser(authenticatedUser); setShowAuth(false); getDashboard().then(setDashboard).catch(() => setApiError("Dashboard data could not be loaded.")); getPracticeProblems().then(setPracticeProblems).catch(() => setApiError("Practice problems could not be loaded.")); }} />}
    </div>
  );
}
