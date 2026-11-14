from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


class CodeRunnerError(ValueError):
    """Raised when a requested language cannot be executed locally."""


@dataclass(frozen=True)
class RunResult:
    status: str
    stdout: str
    stderr: str
    duration_ms: int


MAX_OUTPUT = 10_000
TIMEOUT_SECONDS = 3


def _tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise CodeRunnerError(f"{name} is not installed on the API host")
    return path


def run_code(language: str, code: str, stdin: str) -> RunResult:
    language = language.lower()
    with tempfile.TemporaryDirectory(prefix="learn2code-run-") as directory:
        root = Path(directory)
        if language == "python":
            source = root / "main.py"
            command = [_tool("python3"), "-I", str(source)]
        elif language == "javascript":
            source = root / "main.js"
            command = [_tool("node"), str(source)]
        elif language == "c":
            source = root / "main.c"
            binary = root / "main"
            command = [_tool("sh"), "-c", f"{_tool('cc')} {source} -O2 -o {binary} && {binary}"]
        elif language == "cpp":
            source = root / "main.cpp"
            binary = root / "main"
            command = [_tool("sh"), "-c", f"{_tool('c++')} {source} -O2 -std=c++17 -o {binary} && {binary}"]
        elif language == "java":
            source = root / "Main.java"
            command = [_tool("sh"), "-c", f"{_tool('javac')} {source} && {_tool('java')} -cp {root} Main"]
        elif language == "csharp":
            raise CodeRunnerError("C# execution requires a configured dotnet sandbox")
        else:
            raise CodeRunnerError("This language is not supported by the local runner")

        source.write_text(code, encoding="utf-8")
        environment = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(root),
            "LANG": "C.UTF-8",
        }
        try:
            completed = subprocess.run(
                command,
                input=stdin,
                text=True,
                capture_output=True,
                cwd=root,
                env=environment,
                timeout=TIMEOUT_SECONDS,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            return RunResult("time_limit_exceeded", (error.stdout or "")[:MAX_OUTPUT], "Execution timed out after 3 seconds.", 3000)
        output = (completed.stdout or "")[:MAX_OUTPUT]
        error = (completed.stderr or "")[:MAX_OUTPUT]
        status = "accepted" if completed.returncode == 0 else "runtime_error"
        return RunResult(status, output, error, 0)
