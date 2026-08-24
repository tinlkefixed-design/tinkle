from __future__ import annotations
import os, re, subprocess, sys, tempfile, textwrap, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass(frozen=True)
class SandboxPolicy:
    timeout_ms: int = 5000
    cpu_seconds: int = 2
    memory_mb: int = 128
    max_output_bytes: int = 64 * 1024
    max_file_bytes: int = 2 * 1024 * 1024
    max_processes: int = 1
    network: bool = False

@dataclass(frozen=True)
class SandboxResult:
    ok: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int | None = None
    duration_ms: float = 0.0
    error: str | None = None

class SandboxRunner:
    """Run untrusted Python in a disposable subprocess with OS resource limits.

    The local backend uses POSIX rlimits and a private temporary working directory.
    Network isolation is policy-enforced by removing proxy/environment hints; hard
    kernel network isolation is only available when a container/unshare backend is
    configured. Therefore this runner never claims kernel-level network isolation.
    """
    def __init__(self, policy: SandboxPolicy | None = None):
        self.policy = policy or SandboxPolicy()

    def _preexec(self):
        import resource
        p = self.policy
        resource.setrlimit(resource.RLIMIT_CPU, (p.cpu_seconds, p.cpu_seconds))
        resource.setrlimit(resource.RLIMIT_AS, (p.memory_mb * 1024 * 1024, p.memory_mb * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_FSIZE, (p.max_file_bytes, p.max_file_bytes))
        resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
        resource.setrlimit(resource.RLIMIT_NPROC, (p.max_processes, p.max_processes))

    def _preflight(self, code: str) -> str | None:
        # Defense-in-depth for the local backend. This is not a substitute for
        # kernel/container isolation, so callers must not treat it as a formal
        # sandbox boundary. It blocks common direct filesystem/process/network
        # escape primitives before execution.
        blocked = [
            r"/(?:etc|proc|sys|dev|root)(?:/|$)",
            r"\b(?:subprocess|multiprocessing|socket|ctypes|resource)\b",
            r"\b(?:os\.(?:system|popen|exec|spawn|fork)|shutil\.rmtree)\b",
        ]
        for pattern in blocked:
            if re.search(pattern, code):
                return "Sandbox preflight blocked a restricted operation"
        return None

    def run_python(self, code: str, *, inputs: dict[str, Any] | None = None) -> SandboxResult:
        if not isinstance(code, str) or not code.strip():
            return SandboxResult(False, error="Sandbox code must be non-empty")
        preflight_error = self._preflight(code)
        if preflight_error:
            return SandboxResult(False, error=preflight_error)
        if len(code.encode()) > 128 * 1024:
            return SandboxResult(False, error="Sandbox code exceeds 128 KiB")
        payload = "import json\n_inputs = json.loads(" + repr(__import__('json').dumps(inputs or {})) + ")\n" + code
        start = time.perf_counter()
        with tempfile.TemporaryDirectory(prefix="tinkle-sbx-") as td:
            env = {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUNBUFFERED": "1",
                "HOME": td,
                "TMPDIR": td,
            }
            # Deliberately do not pass API keys, cloud credentials, proxy settings, etc.
            try:
                cp = subprocess.run(
                    [sys.executable, "-I", "-S", "-c", payload],
                    cwd=td, env=env, stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, timeout=self.policy.timeout_ms / 1000,
                    preexec_fn=self._preexec if os.name == "posix" else None,
                    start_new_session=True,
                )
            except subprocess.TimeoutExpired as exc:
                return SandboxResult(False, stdout=(exc.stdout or "")[:self.policy.max_output_bytes],
                                     stderr=(exc.stderr or "")[:self.policy.max_output_bytes],
                                     duration_ms=(time.perf_counter()-start)*1000,
                                     error="Sandbox execution timed out")
            except Exception as exc:
                return SandboxResult(False, duration_ms=(time.perf_counter()-start)*1000,
                                     error=f"Sandbox launch failed: {exc}")
            out, err = cp.stdout[:self.policy.max_output_bytes], cp.stderr[:self.policy.max_output_bytes]
            ok = cp.returncode == 0
            return SandboxResult(ok, out, err, cp.returncode,
                                 (time.perf_counter()-start)*1000,
                                 None if ok else f"Sandbox process exited with code {cp.returncode}")
