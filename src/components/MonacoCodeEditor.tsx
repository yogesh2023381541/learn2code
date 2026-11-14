import { useEffect, useRef, useState } from "react";
import Editor, { type OnMount } from "@monaco-editor/react";
import { Check, Maximize2, Minimize2, RotateCcw, Settings2 } from "lucide-react";

type MonacoCodeEditorProps = {
  value: string;
  language: string;
  storageKey: string;
  starterCode: string;
  onChange: (value: string) => void;
};

const languageMap: Record<string, string> = {
  python: "python",
  javascript: "javascript",
  typescript: "typescript",
  java: "java",
  c: "c",
  cpp: "cpp",
  csharp: "csharp",
};

export function MonacoCodeEditor({ value, language, storageKey, starterCode, onChange }: MonacoCodeEditorProps) {
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [fontSize, setFontSize] = useState(13);
  const [minimap, setMinimap] = useState(false);

  useEffect(() => {
    const saved = window.localStorage.getItem(storageKey);
    if (saved !== null && saved !== value) onChange(saved);
  }, [storageKey]);

  useEffect(() => {
    const timer = window.setTimeout(() => window.localStorage.setItem(storageKey, value), 400);
    return () => window.clearTimeout(timer);
  }, [storageKey, value]);

  function handleMount(editor: Parameters<OnMount>[0]) {
    editorRef.current = editor;
    editor.addCommand(2048 | 49, () => {
      void editor.getAction("editor.action.formatDocument")?.run();
    });
  }

  function resetCode() {
    if (window.confirm("Reset this language draft to the starter code?")) onChange(starterCode);
  }

  return (
    <div className={`monaco-editor-shell ${isFullscreen ? "is-fullscreen" : ""}`}>
      <div className="monaco-toolbar">
        <span className="monaco-toolbar-label">Workspace</span>
        <div className="monaco-toolbar-actions">
          <button type="button" title="Format code" onClick={() => void editorRef.current?.getAction("editor.action.formatDocument")?.run()}><Check size={14} />Format</button>
          <button type="button" title="Reset code" onClick={resetCode}><RotateCcw size={14} />Reset</button>
          <button type="button" title="Editor settings" onClick={() => setShowSettings((current) => !current)}><Settings2 size={14} />Settings</button>
          <button type="button" title="Toggle fullscreen" onClick={() => setIsFullscreen((current) => !current)}>{isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}</button>
        </div>
      </div>
      {showSettings && <div className="monaco-settings">
        <label>Font size <input type="range" min="11" max="20" value={fontSize} onChange={(event) => setFontSize(Number(event.target.value))} /> {fontSize}px</label>
        <label><input type="checkbox" checked={minimap} onChange={(event) => setMinimap(event.target.checked)} /> Minimap</label>
      </div>}
      <div className="monaco-canvas">
        <Editor
          height="100%"
          theme="vs-dark"
          language={languageMap[language] ?? language}
          value={value}
          onChange={(nextValue) => onChange(nextValue ?? "")}
          onMount={handleMount}
          options={{
            automaticLayout: true,
            bracketPairColorization: { enabled: true },
            codeLens: false,
            folding: true,
            fontSize,
            formatOnPaste: true,
            formatOnType: true,
            lineNumbers: "on",
            minimap: { enabled: minimap },
            padding: { top: 12, bottom: 12 },
            scrollBeyondLastLine: false,
            tabSize: 4,
          }}
        />
      </div>
    </div>
  );
}
