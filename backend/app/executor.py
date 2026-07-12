from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import tempfile
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from .catalog import get_method
from .expressions import ContractValidationError, evaluate_contract
from .source_generator import EXECUTABLE_LANGUAGES, generate_source

COMMANDS: dict[str, list[str]] = {
    "python": ["python3"],
    "javascript": ["node"],
    "typescript": ["tsc", "node"],
    "c": ["gcc"],
    "cpp": ["g++"],
    "fortran": ["gfortran"],
    "rust": ["rustc"],
    "go": ["go"],
}


class ExecutionError(RuntimeError):
    def __init__(self, message: str, *, code: str = "execution_error", details: dict[str, Any] | None = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _command_exists(command: str) -> bool:
    return shutil.which(command) is not None


@lru_cache(maxsize=32)
def _runtime_version(language: str) -> str | None:
    probes = {
        "python": ["python3", "--version"],
        "javascript": ["node", "--version"],
        "typescript": ["tsc", "--version"],
        "c": ["gcc", "--version"],
        "cpp": ["g++", "--version"],
        "fortran": ["gfortran", "--version"],
        "rust": ["rustc", "--version"],
        "go": ["go", "version"],
    }
    command = probes.get(language)
    if not command or not _command_exists(command[0]):
        return None
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=3, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    line = (result.stdout or result.stderr).strip().splitlines()
    return line[0][:240] if line else None


def language_registry() -> dict[str, dict[str, Any]]:
    labels = {
        "python": "Python",
        "r": "R",
        "julia": "Julia",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "sql": "SQL",
        "c": "C",
        "cpp": "C++",
        "fortran": "Fortran",
        "rust": "Rust",
        "go": "Go",
        "haskell": "Haskell",
    }
    rows: dict[str, dict[str, Any]] = {}
    for language, label in labels.items():
        commands = COMMANDS.get(language, [])
        available = language in EXECUTABLE_LANGUAGES and bool(commands) and all(_command_exists(command) for command in commands)
        rows[language] = {
            "id": language,
            "label": label,
            "executionMode": "native" if language in EXECUTABLE_LANGUAGES else "source-only",
            "available": available,
            "runtimeVersion": _runtime_version(language),
            "curatedOnly": True,
        }
    return rows


def _limit_command(command: list[str], timeout: int, *, compile_step: bool) -> list[str]:
    """Apply Linux child limits without using subprocess.preexec_fn.

    preexec_fn is unsafe when the API or local job fallback launches work from
    threads. GNU prlimit applies limits in the child process before exec while
    remaining compatible with threaded FastAPI and RQ execution. macOS local
    development falls back to the subprocess timeout and OS-level limits.
    Render container memory and CPU limits remain the authoritative production
    boundary.
    """
    if platform.system() != "Linux" or os.getenv("SC_LAB_USE_PRLIMIT", "1") == "0":
        return command
    prlimit = shutil.which("prlimit")
    if not prlimit:
        return command

    cpu_soft = max(2, int(timeout))
    cpu_hard = cpu_soft + 1
    file_bytes = (128 if compile_step else 4) * 1024 * 1024
    limited = [
        prlimit,
        f"--cpu={cpu_soft}:{cpu_hard}",
        f"--fsize={file_bytes}:{file_bytes}",
        "--nofile=256:256",
    ]

    # Address-space limiting is opt-in because compilers and language runtimes
    # can reserve large virtual ranges even when their resident memory is low.
    # Render service/container memory remains the primary production limit.
    memory_mb = os.getenv("SC_LAB_CHILD_MEMORY_MB", "").strip()
    if memory_mb:
        try:
            memory_bytes = max(128, int(memory_mb)) * 1024 * 1024
            limited.append(f"--as={memory_bytes}:{memory_bytes}")
        except ValueError:
            pass

    return [*limited, "--", *command]


def _safe_environment(workdir: Path) -> dict[str, str]:
    keep = {"PATH", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR"}
    env = {key: value for key, value in os.environ.items() if key in keep}
    env.update(
        {
            "HOME": str(workdir),
            "TMPDIR": str(workdir),
            "GOCACHE": str(workdir / ".gocache"),
            "GOMODCACHE": str(workdir / ".gomodcache"),
            "GONOSUMDB": "*",
            "GOPROXY": "off",
            "GOMAXPROCS": "2",
            "GOFLAGS": "-p=1",
            "NO_PROXY": "*",
            "HTTP_PROXY": "",
            "HTTPS_PROXY": "",
            "ALL_PROXY": "",
            "OPENBLAS_NUM_THREADS": "1",
            "OMP_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    return env


def _run_command(command: list[str], workdir: Path, timeout: int, *, compile_step: bool = False) -> subprocess.CompletedProcess[str]:
    phase = "compile" if compile_step else "execution"
    limited_command = _limit_command(command, timeout, compile_step=compile_step)
    try:
        return subprocess.run(
            limited_command,
            cwd=workdir,
            env=_safe_environment(workdir),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            start_new_session=(os.name == "posix"),
        )
    except subprocess.TimeoutExpired as exc:
        raise ExecutionError(
            f"The {phase} step exceeded {timeout} seconds.",
            code="timeout",
        ) from exc
    except (OSError, subprocess.SubprocessError) as exc:
        raise ExecutionError(
            f"The {phase} process could not be started.",
            code="process_start_error",
            details={"type": type(exc).__name__, "message": str(exc), "command": command[0] if command else None},
        ) from exc


def _compile_and_run(language: str, source_path: Path, timeout: int) -> tuple[str, str, float, float]:
    workdir = source_path.parent
    compile_ms = 0.0
    if language == "python":
        run_command = ["python3", "-S", source_path.name]
    elif language == "javascript":
        run_command = ["node", source_path.name]
    elif language == "typescript":
        outdir = workdir / "compiled"
        outdir.mkdir(exist_ok=True)
        command = ["tsc", "--target", "ES2020", "--module", "commonjs", "--outDir", str(outdir), source_path.name]
        start = time.perf_counter()
        compiled = _run_command(command, workdir, min(20, timeout + 8), compile_step=True)
        compile_ms = (time.perf_counter() - start) * 1000
        if compiled.returncode != 0:
            raise ExecutionError("TypeScript compilation failed.", code="compile_error", details={"stderr": compiled.stderr[-4000:]})
        run_command = ["node", str(outdir / "method.js")]
    elif language == "c":
        binary = workdir / "method-c"
        command = ["gcc", "-std=c11", "-O2", source_path.name, "-lm", "-o", str(binary)]
        start = time.perf_counter(); compiled = _run_command(command, workdir, min(20, timeout + 8), compile_step=True); compile_ms = (time.perf_counter() - start) * 1000
        if compiled.returncode != 0:
            raise ExecutionError("C compilation failed.", code="compile_error", details={"stderr": compiled.stderr[-4000:]})
        run_command = [str(binary)]
    elif language == "cpp":
        binary = workdir / "method-cpp"
        command = ["g++", "-std=c++20", "-O2", source_path.name, "-o", str(binary)]
        start = time.perf_counter(); compiled = _run_command(command, workdir, min(20, timeout + 8), compile_step=True); compile_ms = (time.perf_counter() - start) * 1000
        if compiled.returncode != 0:
            raise ExecutionError("C++ compilation failed.", code="compile_error", details={"stderr": compiled.stderr[-4000:]})
        run_command = [str(binary)]
    elif language == "fortran":
        binary = workdir / "method-fortran"
        command = ["gfortran", "-O2", source_path.name, "-o", str(binary)]
        start = time.perf_counter(); compiled = _run_command(command, workdir, min(20, timeout + 8), compile_step=True); compile_ms = (time.perf_counter() - start) * 1000
        if compiled.returncode != 0:
            raise ExecutionError("Fortran compilation failed.", code="compile_error", details={"stderr": compiled.stderr[-4000:]})
        run_command = [str(binary)]
    elif language == "rust":
        binary = workdir / "method-rust"
        command = ["rustc", "-O", source_path.name, "-o", str(binary)]
        start = time.perf_counter(); compiled = _run_command(command, workdir, min(30, timeout + 15), compile_step=True); compile_ms = (time.perf_counter() - start) * 1000
        if compiled.returncode != 0:
            raise ExecutionError("Rust compilation failed.", code="compile_error", details={"stderr": compiled.stderr[-4000:]})
        run_command = [str(binary)]
    elif language == "go":
        binary = workdir / "method-go"
        command = ["go", "build", "-trimpath", "-o", str(binary), source_path.name]
        start = time.perf_counter(); compiled = _run_command(command, workdir, min(30, timeout + 15), compile_step=True); compile_ms = (time.perf_counter() - start) * 1000
        if compiled.returncode != 0:
            raise ExecutionError("Go compilation failed.", code="compile_error", details={"stderr": compiled.stderr[-4000:]})
        run_command = [str(binary)]
    else:
        raise ExecutionError(f"Native execution is unavailable for {language}.", code="unsupported_language")

    start = time.perf_counter()
    completed = _run_command(run_command, workdir, timeout, compile_step=False)
    execution_ms = (time.perf_counter() - start) * 1000
    if completed.returncode != 0:
        raise ExecutionError(
            f"{language} execution failed.",
            code="runtime_error",
            details={"stderr": completed.stderr[-4000:], "returnCode": completed.returncode},
        )
    if len(completed.stdout.encode("utf-8")) > 65536:
        raise ExecutionError("Execution output exceeded the 64 KiB limit.", code="output_limit")
    return completed.stdout, completed.stderr, compile_ms, execution_ms


def _parse_outputs(stdout: str) -> dict[str, float]:
    outputs: dict[str, float] = {}
    for line in stdout.splitlines():
        if not line.startswith("SC_RESULT "):
            continue
        payload = line[len("SC_RESULT ") :].strip()
        if payload.startswith("{"):
            data = json.loads(payload)
            outputs.update({str(key): float(value) for key, value in data.items()})
        elif "=" in payload:
            key, value = payload.split("=", 1)
            outputs[key.strip()] = float(value.strip().replace("D", "E").replace("d", "e"))
    if not outputs:
        raise ExecutionError("The curated program did not return a structured result.", code="invalid_output")
    return outputs


def compare_outputs(reference: dict[str, float], actual: dict[str, float], absolute_tolerance: float = 1e-10, relative_tolerance: float = 1e-9) -> dict[str, Any]:
    rows = []
    passed = True
    for output_id, expected in reference.items():
        value = actual.get(output_id)
        if value is None:
            row = {"output": output_id, "expected": expected, "actual": None, "absoluteDifference": None, "relativeDifference": None, "tolerance": None, "passed": False}
        else:
            difference = abs(value - expected)
            relative = difference / max(abs(expected), 1e-300)
            tolerance = max(absolute_tolerance, relative_tolerance * abs(expected))
            row = {"output": output_id, "expected": expected, "actual": value, "absoluteDifference": difference, "relativeDifference": relative, "tolerance": tolerance, "passed": difference <= tolerance}
        passed = passed and bool(row["passed"])
        rows.append(row)
    return {"passed": passed, "rows": rows, "absoluteTolerance": absolute_tolerance, "relativeTolerance": relative_tolerance}


def execute_method(
    method_id: str,
    language: str,
    supplied_inputs: dict[str, float],
    timeout_seconds: int = 8,
    include_source: bool = False,
    *,
    absolute_tolerance: float = 1e-10,
    relative_tolerance: float = 1e-9,
) -> dict[str, Any]:
    contract = get_method(method_id)
    if language not in contract.get("languages", []):
        raise ExecutionError(f"{language} is not declared for {method_id}.", code="unsupported_language")
    registry = language_registry()
    language_state = registry.get(language)
    if not language_state or not language_state["available"]:
        raise ExecutionError(
            f"The {language} runtime is not available on this worker.",
            code="runtime_unavailable",
            details={"language": language, "runtime": language_state},
        )
    try:
        inputs, reference = evaluate_contract(contract, supplied_inputs)
    except ContractValidationError as exc:
        raise ExecutionError(str(exc), code="invalid_input") from exc

    filename, source = generate_source(contract, language, inputs)
    with tempfile.TemporaryDirectory(prefix="sc-lab-exec-") as temp:
        workdir = Path(temp)
        source_path = workdir / filename
        source_path.write_text(source, encoding="utf-8")
        stdout, stderr, compile_ms, execution_ms = _compile_and_run(language, source_path, timeout_seconds)
    outputs = _parse_outputs(stdout)
    validation = compare_outputs(reference, outputs, absolute_tolerance, relative_tolerance)
    response: dict[str, Any] = {
        "schema": "sc-lab-execution/1.0",
        "serviceVersion": "0.9.3",
        "methodId": method_id,
        "methodVersion": contract.get("version"),
        "language": language,
        "runtime": "native",
        "runtimeVersion": language_state.get("runtimeVersion"),
        "status": "VALIDATED" if validation["passed"] else "MISMATCH",
        "inputs": inputs,
        "outputs": outputs,
        "referenceOutputs": reference,
        "validation": validation,
        "compileTimeMs": round(compile_ms, 3),
        "executionTimeMs": round(execution_ms, 3),
        "inputFingerprint": canonical_hash({"methodId": method_id, "methodVersion": contract.get("version"), "inputs": inputs}),
        "outputFingerprint": canonical_hash(outputs),
        "sourceFingerprint": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "environment": {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "python": platform.python_version(),
        },
        "warnings": [],
        "executedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if include_source:
        response["source"] = source
        response["filename"] = filename
    if stderr.strip():
        response["warnings"].append("The runtime wrote diagnostic text to stderr.")
    return response


def compare_languages(
    method_id: str,
    languages: list[str],
    inputs: dict[str, float],
    timeout_seconds: int = 8,
    include_source: bool = False,
    absolute_tolerance: float = 1e-10,
    relative_tolerance: float = 1e-9,
) -> dict[str, Any]:
    contract = get_method(method_id)
    validated_inputs, reference = evaluate_contract(contract, inputs)
    executions: list[dict[str, Any]] = []
    for language in languages:
        try:
            executions.append(
                execute_method(
                    method_id,
                    language,
                    validated_inputs,
                    timeout_seconds,
                    include_source,
                    absolute_tolerance=absolute_tolerance,
                    relative_tolerance=relative_tolerance,
                )
            )
        except ExecutionError as exc:
            executions.append(
                {
                    "methodId": method_id,
                    "language": language,
                    "status": "UNAVAILABLE" if exc.code == "runtime_unavailable" else "FAILED",
                    "error": {"code": exc.code, "message": str(exc), "details": exc.details},
                }
            )
    successful = [item for item in executions if item.get("status") in {"VALIDATED", "MISMATCH"}]
    return {
        "schema": "sc-lab-language-comparison/1.0",
        "serviceVersion": "0.9.3",
        "methodId": method_id,
        "methodVersion": contract.get("version"),
        "inputs": validated_inputs,
        "referenceOutputs": reference,
        "languagesRequested": languages,
        "executions": executions,
        "passed": bool(successful) and all(item.get("status") == "VALIDATED" for item in successful),
        "successfulCount": len(successful),
        "comparedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "comparisonFingerprint": canonical_hash({"methodId": method_id, "inputs": validated_inputs, "executions": [{"language": item.get("language"), "outputs": item.get("outputs"), "status": item.get("status")} for item in executions]}),
    }
