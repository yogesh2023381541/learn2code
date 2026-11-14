import { useEffect, useState } from "react";
import {
  createAdminProblem, deleteAdminProblem, downloadAdminProblems, getAdminDashboard, getAdminProblems, getAdminTestCases, getCodingAnalytics, getSubmissions, updateAdminProblem,
  importAdminProblems, replaceAdminTestCases, type AdminTestCase, type PracticeProblem,
} from "../api";

export function SubmissionHistoryPage() {
  const [rows, setRows] = useState<Array<{ id: number; problem_title: string; status: string; language: string; duration_ms: number; memory_kb: number; submitted_at: string }>>([]);
  const [error, setError] = useState("");
  useEffect(() => { getSubmissions().then(setRows).catch((reason) => setError(reason instanceof Error ? reason.message : "Could not load submissions.")); }, []);
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">CODING ACTIVITY</p><h1>Submission history</h1><p className="muted">Every attempt, verdict, and execution metric in one place.</p></div></div>{error && <p className="auth-error">{error}</p>}<div className="problem-table">{rows.length === 0 ? <p className="muted">No submissions yet.</p> : rows.map((row) => <div className="problem-row" key={row.id}><strong>{row.problem_title}</strong><span className={`problem-difficulty ${row.status}`}>{row.status.replaceAll("_", " ")}</span><span>{row.language}</span><span>{row.duration_ms}ms · {row.memory_kb}KB</span><span className="muted">{new Date(row.submitted_at).toLocaleString()}</span></div>)}</div></section>;
}

export function CodingAnalyticsPage() {
  const [data, setData] = useState<Awaited<ReturnType<typeof getCodingAnalytics>> | null>(null);
  useEffect(() => { getCodingAnalytics().then(setData).catch(() => undefined); }, []);
  if (!data) return <section className="alternate-view"><p className="muted">Loading coding analytics…</p></section>;
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">PERFORMANCE</p><h1>Coding analytics</h1><p className="muted">See which topics and languages are building your problem-solving muscle.</p></div></div><div className="practice-stats"><div><strong>{data.attempted}</strong><span>Problems attempted</span></div><div><strong>{data.solved}</strong><span>Problems solved</span></div><div><strong>{data.acceptance_rate}%</strong><span>Acceptance rate</span></div><div><strong>{data.total_submissions}</strong><span>Total submissions</span></div></div><div className="lower-grid"><section className="activity-panel"><h3>Difficulty progress</h3>{Object.entries(data.by_difficulty).map(([name, value]) => <div className="analytics-row" key={name}><span>{name}</span><div className="progress-track"><div style={{ width: `${value.attempted ? (value.solved / value.attempted) * 100 : 0}%` }} /></div><b>{value.solved}/{value.attempted}</b></div>)}</section><section className="activity-panel"><h3>Languages used</h3>{Object.entries(data.by_language).map(([name, count]) => <div className="analytics-row" key={name}><span>{name}</span><b>{count} submissions</b></div>)}</section></div></section>;
}

function TestCaseManager({ problemId }: { problemId: number }) {
  const [cases, setCases] = useState<AdminTestCase[]>([]);
  const [message, setMessage] = useState("");
  useEffect(() => { getAdminTestCases(problemId).then(setCases).catch(() => setMessage("Test cases could not be loaded.")); }, [problemId]);
  function update(index: number, field: keyof AdminTestCase, value: string | boolean) {
    setCases((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, [field]: value } : item));
  }
  async function save() {
    try { await replaceAdminTestCases(problemId, cases); setMessage("Test cases saved."); }
    catch (reason) { setMessage(reason instanceof Error ? reason.message : "Test cases could not be saved."); }
  }
  return <div className="admin-import-card"><div className="section-heading"><h3>Test cases</h3><button className="primary-button" onClick={() => void save()}>Save tests</button></div>{cases.map((item, index) => <div className="test-case-editor" key={item.id ?? index}><textarea value={item.stdin} placeholder="Standard input" onChange={(event) => update(index, "stdin", event.target.value)} /><textarea value={item.expected_stdout} placeholder="Expected output" onChange={(event) => update(index, "expected_stdout", event.target.value)} /><label><input type="checkbox" checked={item.is_hidden} onChange={(event) => update(index, "is_hidden", event.target.checked)} /> Hidden</label><button className="text-button" onClick={() => setCases((current) => current.filter((_, itemIndex) => itemIndex !== index))}>Remove</button></div>)}<button className="secondary-button" onClick={() => setCases((current) => [...current, { stdin: "", expected_stdout: "", is_hidden: false, time_limit_ms: 3000, memory_limit_mb: 256 }])}>Add test case</button>{message && <p className="muted">{message}</p>}</div>;
}

export function AdminPage() {
  const [dashboard, setDashboard] = useState<Awaited<ReturnType<typeof getAdminDashboard>> | null>(null);
  const [problems, setProblems] = useState<PracticeProblem[]>([]);
  const [message, setMessage] = useState("");
  const [fileFormat, setFileFormat] = useState<"json" | "csv">("json");
  const [newProblem, setNewProblem] = useState({ title: "", slug: "", description: "", difficulty: "Easy", category: "Arrays" });
  const [testCaseProblemId, setTestCaseProblemId] = useState<number | null>(null);
  useEffect(() => { Promise.all([getAdminDashboard(), getAdminProblems()]).then(([summary, items]) => { setDashboard(summary); setProblems(items); }).catch((reason) => setMessage(reason instanceof Error ? reason.message : "Admin data could not be loaded.")); }, []);
  async function importFile(file: File) {
    try {
      const result = await importAdminProblems(fileFormat, await file.text());
      setMessage(`Imported ${result.imported_count}, skipped ${result.skipped_count}, errors ${result.error_count}.`);
      setDashboard(await getAdminDashboard());
      setProblems(await getAdminProblems());
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Import failed."); }
  }
  async function removeProblem(id: number) {
    if (!window.confirm("Delete this problem and its test cases?")) return;
    await deleteAdminProblem(id);
    setProblems((current) => current.filter((problem) => problem.id !== id));
    setMessage("Problem deleted.");
  }
  async function togglePublished(problem: PracticeProblem) {
    try {
      const updated = await updateAdminProblem(problem, problem.is_published === false);
      setProblems((current) => current.map((item) => item.id === updated.id ? updated : item));
      setDashboard(await getAdminDashboard());
      setMessage(updated.is_published ? "Problem published for learners." : "Problem moved back to draft.");
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Publication status could not be changed."); }
  }
  async function createProblem() {
    try {
      const created = await createAdminProblem(newProblem);
      setProblems((current) => [created, ...current]);
      setNewProblem({ title: "", slug: "", description: "", difficulty: "Easy", category: "Arrays" });
      setMessage("Problem created.");
    } catch (reason) { setMessage(reason instanceof Error ? reason.message : "Problem could not be created."); }
  }
  return <section className="alternate-view"><div className="page-heading"><div><p className="eyebrow">ADMIN CONSOLE</p><h1>Problem management</h1><p className="muted">Import authorized content, review the catalog, and manage publication.</p></div></div>{dashboard && <div className="practice-stats"><div><strong>{dashboard.total_problems}</strong><span>Total problems</span></div><div><strong>{dashboard.published_problems}</strong><span>Published</span></div><div><strong>{dashboard.total_submissions}</strong><span>Submissions</span></div><div><strong>{dashboard.imports}</strong><span>Imports</span></div></div>}<div className="admin-import-card"><h3>Create problem</h3><div className="admin-form-grid"><input placeholder="Title" value={newProblem.title} onChange={(event) => setNewProblem({ ...newProblem, title: event.target.value })} /><input placeholder="slug-like-this" value={newProblem.slug} onChange={(event) => setNewProblem({ ...newProblem, slug: event.target.value })} /><input placeholder="Category" value={newProblem.category} onChange={(event) => setNewProblem({ ...newProblem, category: event.target.value })} /><select value={newProblem.difficulty} onChange={(event) => setNewProblem({ ...newProblem, difficulty: event.target.value })}><option>Easy</option><option>Medium</option><option>Hard</option></select><textarea placeholder="Description" value={newProblem.description} onChange={(event) => setNewProblem({ ...newProblem, description: event.target.value })} /></div><button className="primary-button" onClick={() => void createProblem()}>Create problem</button></div><div className="admin-import-card"><h3>Bulk import</h3><p className="muted">Use authorized JSON or CSV data. Duplicate slugs are skipped by default.</p><div className="editor-actions"><select value={fileFormat} onChange={(event) => setFileFormat(event.target.value as "json" | "csv")}><option value="json">JSON</option><option value="csv">CSV</option></select><input type="file" accept={`.${fileFormat}`} onChange={(event) => { const file = event.target.files?.[0]; if (file) void importFile(file); }} /><button className="secondary-button" onClick={() => void downloadAdminProblems(fileFormat, true)}>Download template</button><button className="secondary-button" onClick={() => void downloadAdminProblems(fileFormat)}>Export catalog</button></div></div>{message && <p className="auth-error" role="status">{message}</p>}<div className="problem-table">{problems.map((problem) => <div className="problem-row" key={problem.id}><strong>{problem.title}</strong><span>{problem.difficulty}</span><span>{problem.category}</span><span>{problem.is_published === false ? "Draft" : "Published"}</span><button className="text-button" onClick={() => void togglePublished(problem)}>{problem.is_published === false ? "Publish" : "Unpublish"}</button><button className="text-button" onClick={() => setTestCaseProblemId(problem.id)}>Tests</button><button className="text-button" onClick={() => void removeProblem(problem.id)}>Delete</button></div>)}</div>{testCaseProblemId && <TestCaseManager problemId={testCaseProblemId} />}</section>;
}
