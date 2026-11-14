import { useState, type FormEvent } from "react";
import { authenticate, saveOnboarding } from "./api";

type Subject = {
  name: string;
  category: string;
  description: string;
  progress: number;
  lessons: number;
  duration: string;
  color: string;
  icon: string;
};

const subjects: Subject[] = [
  { name: "Python", category: "Programming", description: "Build a strong foundation with Python fundamentals and real projects.", progress: 68, lessons: 42, duration: "18h", color: "violet", icon: "Py" },
  { name: "Data Structures & Algorithms", category: "Computer science", description: "Master problem solving patterns that power great engineering interviews.", progress: 34, lessons: 56, duration: "32h", color: "cyan", icon: "DS" },
  { name: "React", category: "Web development", description: "Create fast, accessible interfaces with modern React and TypeScript.", progress: 12, lessons: 38, duration: "21h", color: "blue", icon: "Re" },
  { name: "SQL & Databases", category: "Backend", description: "Design reliable data models and write queries with confidence.", progress: 0, lessons: 28, duration: "14h", color: "orange", icon: "DB" },
];

const roadmap = [
  { title: "Python basics", subtitle: "Variables & syntax", state: "completed", x: 8, y: 22 },
  { title: "Control flow", subtitle: "Make decisions", state: "completed", x: 29, y: 11 },
  { title: "Data structures", subtitle: "Collections", state: "current", x: 51, y: 28 },
  { title: "Functions", subtitle: "Reusable logic", state: "available", x: 72, y: 13 },
  { title: "OOP", subtitle: "Build abstractions", state: "locked", x: 85, y: 38 },
  { title: "Final project", subtitle: "Ship something real", state: "locked", x: 62, y: 67 },
];

const practiceProblems = [
  { title: "Two Sum", difficulty: "Easy", category: "Arrays", solved: true, success: "48%" },
  { title: "Valid Parentheses", difficulty: "Easy", category: "Stack", solved: true, success: "54%" },
  { title: "Longest Substring Without Repeating Characters", difficulty: "Medium", category: "Strings", solved: false, success: "36%" },
  { title: "Merge Intervals", difficulty: "Medium", category: "Sorting", solved: false, success: "41%" },
  { title: "Trapping Rain Water", difficulty: "Hard", category: "Arrays", solved: false, success: "29%" },
];

function Icon({ children }: { children: string }) {
  return <span className="icon" aria-hidden="true">{children}</span>;
}

function WorkspacePage({ active, subjects, onSelect }: { active: string; subjects: Subject[]; onSelect: (subject: Subject) => void }) {
  if (active === "Explore") {
    return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">LEARNING LIBRARY</p><h1>Explore your next skill</h1><p className="muted">Structured paths built to take you from curious to capable.</p></div><button className="filter-button">All categories <span>⌄</span></button></div><div className="explore-hero"><div><span className="hero-label">CURATED FOR YOU</span><h2>Build skills that<br /><em>compound.</em></h2><p>Choose a path, show up consistently, and let your progress do the talking.</p></div><div className="path-orbit">✦</div></div><div className="section-heading"><div><h3>All subjects</h3><p className="muted">{subjects.length} learning paths available</p></div></div><div className="explore-grid">{subjects.map((subject) => <button className="explore-card" key={subject.name} onClick={() => onSelect(subject)}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><span className="tag">{subject.category}</span><h3>{subject.name}</h3><p>{subject.description}</p><div className="explore-meta"><span>{subject.lessons} lessons</span><span>{subject.duration}</span><b>View path →</b></div></button>)}</div></section>;
  }
  if (active === "Practice") {
    return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">CODING PRACTICE</p><h1>Sharpen your problem solving</h1><p className="muted">Practice deliberately. Build confidence one problem at a time.</p></div><button className="primary-button">My submissions <span>→</span></button></div><div className="practice-stats"><div><strong>47</strong><span>Problems solved</span></div><div><strong>68%</strong><span>Acceptance rate</span></div><div><strong>12</strong><span>Day streak</span></div><div><strong>3</strong><span>Languages used</span></div></div><div className="section-heading"><div><h3>Problem set</h3><p className="muted">Keep your momentum going</p></div><button className="filter-button">All difficulties <span>⌄</span></button></div><div className="problem-table"><div className="problem-header"><span>PROBLEM</span><span>DIFFICULTY</span><span>CATEGORY</span><span>ACCEPTANCE</span><span /></div>{practiceProblems.map((problem) => <button className="problem-row" key={problem.title}><span><i className={problem.solved ? "solved" : ""}>{problem.solved ? "✓" : "○"}</i><strong>{problem.title}</strong></span><span className={`problem-difficulty ${problem.difficulty.toLowerCase()}`}>{problem.difficulty}</span><span className="muted">{problem.category}</span><span className="muted">{problem.success}</span><b>→</b></button>)}</div></section>;
  }
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">YOUR PROGRESS</p><h1>My learning</h1><p className="muted">A clear view of everything you&apos;re building.</p></div><button className="secondary-button">Edit daily goal</button></div><div className="learning-overview"><div className="overview-ring"><strong>44%</strong><span>overall progress</span></div><div><h3>You&apos;re building a habit.</h3><p className="muted">You&apos;ve learned for 24.5 hours across 3 active paths. Keep your 12 day streak alive today.</p><div className="progress-track"><div style={{ width: "44%" }} /></div><small>28 of 64 topics completed</small></div></div><div className="section-heading"><div><h3>Active learning paths</h3><p className="muted">Continue where you left off</p></div></div><div className="my-learning-list">{subjects.map((subject) => <button className="my-learning-row" key={subject.name} onClick={() => onSelect(subject)}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><div><strong>{subject.name}</strong><span>{subject.progress}% complete · {subject.lessons} lessons</span></div><div className="progress-track"><div style={{ width: `${subject.progress}%` }} /></div><b>→</b></button>)}</div></section>;
}

function LessonView({ subject, onClose }: { subject: Subject; onClose: () => void }) {
  const [completed, setCompleted] = useState(false);
  return <div className="lesson-backdrop"><section className="lesson-modal"><header className="lesson-header"><div><button className="back-button" onClick={onClose}>← Back to roadmap</button><p className="eyebrow">MODULE 3 · DATA STRUCTURES</p><h1>Working with collections</h1><p className="muted">{subject.name} · Lesson 28 of {subject.lessons}</p></div><button className="close-button" onClick={onClose}>×</button></header><div className="lesson-progress"><span style={{ width: completed ? "72%" : "68%" }} /></div><div className="lesson-layout"><article className="lesson-content"><div className="video-placeholder"><div className="play-button">▶</div><span>Introduction to collections</span><small>12:48 · HD</small></div><h2>Make your data work for you</h2><p>Collections let you group and organize related values. In Python, the most common collection types are lists, tuples, sets, and dictionaries.</p><h3>Lists and dictionaries</h3><p>Use a list when order matters and a dictionary when you need to look values up by a meaningful key. Choosing the right structure makes your programs easier to reason about.</p><div className="lesson-callout"><strong>Key idea</strong><span>Good data structures reduce the amount of code you need to write.</span></div><button className={`complete-button ${completed ? "done" : ""}`} onClick={() => setCompleted(true)}>{completed ? "✓ Lesson completed" : "Mark lesson as complete"} <span>{completed ? "" : "→"}</span></button></article><aside className="lesson-aside"><div className="aside-section"><span className="eyebrow">ON THIS PAGE</span><button className="aside-link current">Working with collections</button><button className="aside-link">Lists and dictionaries</button><button className="aside-link">Quick knowledge check</button></div><div className="code-example"><div className="code-title"><span>PYTHON</span><span>Copy</span></div><pre><code><span className="code-purple">habits</span> = {'{'}{"\n"}  <span className="code-cyan">&quot;coding&quot;</span>: <span className="code-orange">True</span>,{"\n"}  <span className="code-cyan">&quot;minutes&quot;</span>: <span className="code-orange">45</span>,{"\n"}{'}'}{"\n"}{"\n"}<span className="code-purple">print</span>(habits[<span className="code-cyan">&quot;minutes&quot;</span>])</code></pre></div><div className="next-lesson"><span className="eyebrow">UP NEXT</span><strong>List comprehensions</strong><span>8 min · Not started</span></div></aside></div></section></div>;
}

function AuthDialog({ onClose }: { onClose: () => void }) {
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
      await authenticate(mode, { full_name: fullName, email, password });
      if (mode === "signup") {
        await authenticate("login", { email, password });
        setOnboarding(true);
      } else {
        setSubmitted(true);
      }
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Authentication failed.");
    }
  }

  async function finishOnboarding(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      await saveOnboarding({ experience_level: experience, learning_goal: goal, preferred_language: language, daily_minutes: minutes, subjects: selectedSubjects });
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
  const [active, setActive] = useState("Overview");
  const [selectedSubject, setSelectedSubject] = useState(subjects[0]);
  const [search, setSearch] = useState("");
  const [showRoadmap, setShowRoadmap] = useState(false);
  const [showLesson, setShowLesson] = useState(false);
  const [showAuth, setShowAuth] = useState(false);
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
            <button className={active === item ? "nav-item active" : "nav-item"} onClick={() => setActive(item)} key={item}>
              <Icon>{["⌂", "◈", "▣", "⌘"][index]}</Icon>{item}
              {item === "My learning" && <span className="nav-count">4</span>}
            </button>
          ))}
        </nav>
        <div className="workspace-label library-label">YOUR LIBRARY</div>
        <nav className="nav-list">
          <button className="nav-item"><Icon>☆</Icon>Bookmarks</button>
          <button className="nav-item"><Icon>◷</Icon>History</button>
        </nav>
        <div className="sidebar-bottom">
          <div className="upgrade-card"><span className="sparkle">✦</span><strong>Unlock your potential</strong><p>Get unlimited access to every learning path.</p><button>Explore Pro <span>→</span></button></div>
          <button className="nav-item"><Icon>⚙</Icon>Settings</button>
          <button className="profile-mini" onClick={() => setShowAuth(true)}><div className="avatar">YC</div><div><strong>Yogesh Chavan</strong><small>Free plan · Account</small></div><span className="more">•••</span></button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb"><span>Workspace</span><b>/</b>{active}</div>
          <div className="top-actions"><label className="search"><span>⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search anything..." /><kbd>⌘ K</kbd></label><button className="icon-button">◔</button><button className="icon-button notification">♢<i /></button></div>
        </header>

        <div className={`content ${active === "Overview" ? "" : "alternate"}`}>
          <WorkspacePage active={active} subjects={filteredSubjects} onSelect={(subject) => { setSelectedSubject(subject); setShowRoadmap(true); }} />
          <section className="welcome-row">
            <div><p className="eyebrow">FRIDAY, NOVEMBER 14, 2026</p><h1>Good morning, Yogesh <span>✦</span></h1><p className="muted">Small steps every day lead to big results. Let&apos;s keep building.</p></div>
            <button className="streak"><span>♨</span><strong>12 day streak</strong><small>Keep it going!</small></button>
          </section>

          <section className="hero-card">
            <div className="hero-copy"><div className="hero-label"><span className="pulse-dot" /> CONTINUE LEARNING</div><h2>Python for<br /><em>problem solvers.</em></h2><p>Pick up where you left off. You&apos;re making great progress.</p><div className="hero-progress"><span><b>68%</b> complete</span><span>28 / 42 lessons</span></div><div className="progress-track"><div style={{ width: "68%" }} /></div><button className="primary-button" onClick={() => setShowRoadmap(true)}>Continue lesson <span>→</span></button></div>
            <div className="hero-art" aria-hidden="true"><div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="code-card"><span>def</span> <b>solve</b>(problem):<br /><i>    while</i> not solved:<br /><span>        learn()</span><br />    return <b>growth</b></div><div className="floating-badge badge-one">✦  +1 XP</div><div className="floating-badge badge-two">✓  3 day goal</div></div>
          </section>

          <section className="stats-grid">
            <div className="stat-card"><div className="stat-icon violet-bg">◒</div><div><span>Learning hours</span><strong>24.5 <small>hrs</small></strong><p className="positive">↑ 18% <i>vs last week</i></p></div></div>
            <div className="stat-card"><div className="stat-icon cyan-bg">✓</div><div><span>Topics completed</span><strong>28 <small>/ 64</small></strong><p className="positive">↑ 4 <i>this week</i></p></div></div>
            <div className="stat-card"><div className="stat-icon orange-bg">⌘</div><div><span>Problems solved</span><strong>47</strong><p className="positive">↑ 12 <i>this week</i></p></div></div>
            <div className="stat-card"><div className="stat-icon pink-bg">♨</div><div><span>Current streak</span><strong>12 <small>days</small></strong><p className="muted">Best: 18 days</p></div></div>
          </section>

          <div className="section-heading"><div><h3>Pick up where you left off</h3><p className="muted">Your active learning paths</p></div><button className="text-button">View all <span>→</span></button></div>
          <section className="learning-grid">
            {subjects.slice(0, 3).map((subject) => <button className="learning-card" key={subject.name} onClick={() => { setSelectedSubject(subject); setShowRoadmap(true); }}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><div className="card-top"><span className="tag">{subject.category}</span><span className="bookmark">☆</span></div><h4>{subject.name}</h4><p>{subject.progress === 68 ? "Functions & modules" : subject.progress === 34 ? "Trees & graphs" : "Components & props"}</p><div className="card-progress"><div className="progress-track"><div style={{ width: `${subject.progress}%` }} /></div><span>{subject.progress}%</span></div><div className="card-footer"><span>{subject.lessons} lessons</span><span>→</span></div></button>)}
          </section>

          <div className="section-heading explore-heading"><div><h3>Explore subjects</h3><p className="muted">Find your next thing to learn</p></div><button className="filter-button">All subjects <span>⌄</span></button></div>
          <section className="subject-grid">{filteredSubjects.map((subject) => <button className="subject-row" key={subject.name} onClick={() => { setSelectedSubject(subject); setShowRoadmap(true); }}><div className={`subject-symbol ${subject.color}`}>{subject.icon}</div><div className="subject-info"><strong>{subject.name}</strong><span>{subject.category} · {subject.lessons} lessons</span></div><div className="difficulty"><span className={`difficulty-dot ${subject.progress > 50 ? "green" : ""}`} />{subject.progress > 50 ? "Intermediate" : "Beginner"}</div><span className="subject-time">{subject.duration}</span><span className="arrow">→</span></button>)}</section>

          <div className="lower-grid"><section className="activity-panel"><div className="section-heading"><div><h3>Weekly activity</h3><p className="muted">Your learning rhythm</p></div><span className="week-label">This week ⌄</span></div><div className="chart"><div className="chart-y"><span>4h</span><span>3h</span><span>2h</span><span>1h</span><span>0</span></div><div className="chart-area">{[30, 52, 40, 74, 58, 90, 45].map((height, index) => <div className="bar-column" key={index}><div className={`bar ${index === 5 ? "today" : ""}`} style={{ height: `${height}%` }} /><span>{["M", "T", "W", "T", "F", "S", "S"][index]}</span></div>)}</div></div></section><section className="goals-panel"><div className="section-heading"><div><h3>Today&apos;s goal</h3><p className="muted">Friday, November 14</p></div><span className="goal-percent">75%</span></div><div className="goal-ring"><div><strong>45</strong><span>min left</span></div></div><p className="goal-message">You&apos;re almost there! Finish strong.</p><button className="secondary-button" onClick={() => setShowRoadmap(true)}>View your plan <span>→</span></button></section></div>
        </div>
      </main>

      {showRoadmap && <div className="modal-backdrop" onClick={() => setShowRoadmap(false)}><section className="roadmap-modal" onClick={(event) => event.stopPropagation()}><div className="modal-header"><div><span className="eyebrow">LEARNING PATH</span><h2>{selectedSubject.name} roadmap</h2><p className="muted">Follow the path. Master the craft.</p></div><button className="close-button" onClick={() => setShowRoadmap(false)}>×</button></div><div className="roadmap-toolbar"><span><i className="legend-dot completed" /> Completed</span><span><i className="legend-dot current" /> In progress</span><span><i className="legend-dot locked" /> Locked</span><button>Fit to screen ⛶</button></div><div className="roadmap-canvas"><svg viewBox="0 0 100 80" preserveAspectRatio="none" aria-hidden="true"><path d="M 14 29 C 20 29, 22 17, 34 17 S 43 32, 57 35 S 67 19, 76 19 S 80 46, 88 46 S 78 71, 66 71" /><path className="completed-path" d="M 14 29 C 20 29, 22 17, 34 17 S 43 32, 57 35" /></svg>{roadmap.map((node) => <button className={`roadmap-node ${node.state}`} style={{ left: `${node.x}%`, top: `${node.y}%` }} key={node.title}><span>{node.state === "completed" ? "✓" : node.state === "locked" ? "•" : "→"}</span><strong>{node.title}</strong><small>{node.subtitle}</small></button>)}</div><div className="roadmap-footer"><div><strong>Next up: Data structures</strong><span>Estimated time · 45 min</span></div><button className="primary-button" onClick={() => { setShowRoadmap(false); setShowLesson(true); }}>Start learning <span>→</span></button></div></section></div>}
      {showLesson && <LessonView subject={selectedSubject} onClose={() => setShowLesson(false)} />}
      {showAuth && <AuthDialog onClose={() => setShowAuth(false)} />}
    </div>
  );
}
