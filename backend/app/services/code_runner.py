from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from ..config import settings


class CodeRunnerError(ValueError):
    """Raised when a requested language cannot be executed locally."""


@dataclass(frozen=True)
class RunResult:
    status: str
    stdout: str
    stderr: str
    duration_ms: int
    memory_kb: int = 0


MAX_OUTPUT = 10_000
TIMEOUT_SECONDS = 3
JUDGE0_LANGUAGES = {"c": 50, "cpp": 54, "java": 62, "javascript": 63, "python": 71, "csharp": 51}
DOCKER_IMAGES = {
    "python": ("python:3.14-alpine", ["python", "/workspace/main.py"]),
    "javascript": ("node:22-alpine", ["node", "/workspace/main.js"]),
    "c": ("gcc:14", ["sh", "-c", "cc /workspace/main.c -O2 -o /tmp/main && /tmp/main"]),
    "cpp": ("gcc:14", ["sh", "-c", "c++ /workspace/main.cpp -O2 -std=c++17 -o /tmp/main && /tmp/main"]),
    "java": ("eclipse-temurin:21-jdk", ["sh", "-c", "javac -d /tmp /workspace/Main.java && java -cp /tmp Main"]),
}


def _run_with_judge0(language: str, code: str, stdin: str) -> RunResult:
    language_id = JUDGE0_LANGUAGES.get(language)
    if language_id is None:
        raise CodeRunnerError("This language is not supported by Judge0")
    headers = {"Content-Type": "application/json"}
    if settings.judge0_api_key:
        headers["X-Auth-Token"] = settings.judge0_api_key
    url = settings.judge0_url.rstrip("/")
    try:
        with httpx.Client(timeout=5) as client:
            response = client.post(
                f"{url}/submissions?base64_encoded=false&wait=false",
                headers=headers,
                json={"language_id": language_id, "source_code": code, "stdin": stdin},
            )
            response.raise_for_status()
            token = response.json()["token"]
            deadline = time.monotonic() + settings.judge0_wait_seconds
            while time.monotonic() < deadline:
                result = client.get(
                    f"{url}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                )
                result.raise_for_status()
                body = result.json()
                if body.get("status", {}).get("id", 1) > 2:
                    status_id = body["status"]["id"]
                    status = {
                        3: "accepted", 4: "wrong_answer", 5: "time_limit_exceeded",
                        6: "compilation_error", 7: "runtime_error", 8: "runtime_error",
                    }.get(status_id, "internal_error")
                    return RunResult(
                        status, body.get("stdout") or "",
                        body.get("compile_output") or body.get("stderr") or "",
                        round(float(body.get("time") or 0) * 1000),
                        int(body.get("memory") or 0),
                    )
                time.sleep(0.2)
    except (httpx.HTTPError, KeyError, ValueError) as error:
        raise CodeRunnerError(f"Judge0 execution failed: {error}") from error
    raise CodeRunnerError("Judge0 execution timed out while waiting for a result")


def _run_with_docker(language: str, code: str, stdin: str) -> RunResult:
    image_command = DOCKER_IMAGES.get(language)
    if image_command is None:
        raise CodeRunnerError("This language is not configured for the Docker runner")
    image, program = image_command
    source_name = "Main.java" if language == "java" else f"main.{language if language != 'cpp' else 'cpp'}"
    with tempfile.TemporaryDirectory(prefix="learn2code-docker-") as directory:
        root = Path(directory)
        (root / source_name).write_text(code, encoding="utf-8")
        command = [
            _tool("docker"), "run", "--rm", "--network", "none",
            "--cpus", "1", "--memory", "256m", "--pids-limit", "64",
            "--read-only", "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
            "-i", "-v", f"{root}:/workspace:ro", image, *program,
        ]
        try:
            completed = subprocess.run(
                command, input=stdin, text=True, capture_output=True,
                timeout=TIMEOUT_SECONDS, check=False,
            )
        except subprocess.TimeoutExpired as error:
            return RunResult(
                "time_limit_exceeded", (error.stdout or "")[:MAX_OUTPUT],
                "Execution timed out after 3 seconds.", 3000,
            )
        output = (completed.stdout or "")[:MAX_OUTPUT]
        error = (completed.stderr or "")[:MAX_OUTPUT]
        if completed.returncode == 0:
            status = "accepted"
        elif "error" in error.lower() and language in {"c", "cpp", "java"}:
            status = "compilation_error"
        else:
            status = "runtime_error"
        return RunResult(status, output, error, 0)


def _tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        raise CodeRunnerError(f"{name} is not installed on the API host")
    return path


def run_code(language: str, code: str, stdin: str) -> RunResult:
    language = language.lower()
    if settings.execution_backend == "judge0":
        if not settings.judge0_url:
            raise CodeRunnerError("Judge0 is selected but JUDGE0_URL is not configured")
        return _run_with_judge0(language, code, stdin)
    if settings.execution_backend == "docker":
        return _run_with_docker(language, code, stdin)
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
        if completed.returncode == 0:
            status = "accepted"
        elif language in {"c", "cpp", "java"} and (
            "error:" in error.lower() or "error " in error.lower()
        ):
            status = "compilation_error"
        else:
            status = "runtime_error"
        return RunResult(status, output, error, 0)
