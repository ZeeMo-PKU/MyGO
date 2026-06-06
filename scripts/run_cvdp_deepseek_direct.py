#!/usr/bin/env python3
"""Run CVDP cid003 direct-Verilog evaluation through OpenRouter DeepSeek."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET = ROOT / "cvdp_v1.1.0_nonagentic_code_generation_no_commercial.jsonl"
DEFAULT_CSV = ROOT / "cvdp_code_generation_649_tasks.csv"
DEFAULT_KEY_FILE = Path.home() / "work" / "secrets" / "openrouter_key.txt"
DEFAULT_MODEL = "deepseek/deepseek-v4-pro"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_OUT = Path.home() / "work" / "cvdp-runs" / "direct-deepseek-v4-server-20260606"


SYSTEM_PROMPT = """You are solving a CVDP non-agentic Specification-to-RTL problem.
Return only synthesizable SystemVerilog RTL for the requested file.
Do not include explanations, markdown fences, testbenches, or comments about your reasoning.
Do not assume access to hidden tests or reference answers.
"""


def sanitize_name(name: str, max_len: int = 96) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", name)
    name = re.sub(r"\s+", "_", name).strip("._ ")
    return name[:max_len] or "item"


def read_key(path: Path) -> str:
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        key = path.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(f"API key is empty: {path}")
    return key


def selected_ids(csv_path: Path) -> set[str]:
    with csv_path.open(newline="", encoding="utf-8-sig") as f:
        rows = csv.DictReader(f)
        return {
            row["id"]
            for row in rows
            if row["split"] == "nonagentic_no_commercial"
            and row["categories"].split(";")[0] == "cid003"
        }


def load_tasks(dataset_path: Path, csv_path: Path) -> list[dict]:
    ids = selected_ids(csv_path)
    tasks: list[dict] = []
    with dataset_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("id") not in ids:
                continue

            output = row.get("output", {})
            if output.get("response"):
                raise RuntimeError(f"Non-empty output.response found for {row['id']}")
            for file_name, content in output.get("context", {}).items():
                if content:
                    raise RuntimeError(f"Non-empty output.context found for {row['id']}:{file_name}")
            tasks.append(row)

    tasks.sort(key=lambda r: r["id"])
    if len(tasks) != 78:
        raise RuntimeError(f"Expected 78 cid003 tasks, got {len(tasks)}")
    return tasks


def expected_files(task: dict) -> list[str]:
    files = list(task.get("output", {}).get("context", {}).keys())
    if not files:
        raise RuntimeError(f"No expected output file listed for {task['id']}")
    return files


def build_prompt(task: dict) -> str:
    files = expected_files(task)
    context = task.get("input", {}).get("context", {}) or {}
    prompt = task.get("input", {}).get("prompt", "")
    if not prompt:
        raise RuntimeError(f"Empty prompt for {task['id']}")

    parts = [
        f"Problem ID: {task['id']}",
        f"Category: {', '.join(task.get('categories', []))}",
        "Expected output file(s):",
        "\n".join(f"- {name}" for name in files),
        "",
        "Task:",
        prompt,
    ]
    if context:
        parts.extend(["", "Public input context files:"])
        for name, content in context.items():
            parts.append(f"\nFile: {name}\n```systemverilog\n{content}\n```")
    return "\n".join(parts)


def strip_code_fence(text: str) -> str:
    text = text.strip()
    match = re.search(r"```(?:systemverilog|verilog|sv)?\s*(.*?)```", text, flags=re.I | re.S)
    if match:
        return match.group(1).strip()
    return text


def call_model(client: OpenAI, model: str, prompt: str, timeout: float) -> tuple[str, str, dict]:
    start = time.time()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=20000,
        timeout=timeout,
        extra_body={"reasoning": {"enabled": False, "exclude": True}},
        extra_headers={
            "HTTP-Referer": "https://localhost/cvdp-direct",
            "X-Title": "CVDP DeepSeek direct-Verilog evaluation",
        },
    )
    elapsed = time.time() - start
    msg = resp.choices[0].message
    raw_text = msg.content or ""
    meta = {
        "model": model,
        "elapsed_seconds": elapsed,
        "response_id": getattr(resp, "id", None),
        "finish_reason": getattr(resp.choices[0], "finish_reason", None),
        "usage": getattr(resp, "usage", None).model_dump() if getattr(resp, "usage", None) else {},
    }
    return raw_text, strip_code_fence(raw_text), meta


def call_model_with_retries(
    client: OpenAI,
    model: str,
    prompt: str,
    timeout: float,
    retries: int,
    task_dir: Path,
) -> tuple[str, dict]:
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        (task_dir / f"prompt_sent_to_deepseek_attempt{attempt}.txt").write_text(
            SYSTEM_PROMPT + "\n\n--- USER PROMPT ---\n" + prompt,
            encoding="utf-8",
        )
        try:
            raw_text, rtl_text, meta = call_model(client, model, prompt, timeout)
            (task_dir / f"DeepSeek_raw_response_attempt{attempt}.txt").write_text(
                raw_text,
                encoding="utf-8",
            )
            meta["attempt"] = attempt
            if not rtl_text.strip():
                (task_dir / f"LLM_empty_response_attempt{attempt}.json").write_text(
                    json.dumps(meta, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                raise RuntimeError(
                    f"empty RTL response from model on attempt {attempt}; "
                    f"finish_reason={meta.get('finish_reason')}"
                )
            return rtl_text, meta
        except Exception as exc:
            last_exc = exc
            (task_dir / f"LLM_error_attempt{attempt}.txt").write_text(
                f"{type(exc).__name__}: {exc}",
                encoding="utf-8",
            )
            if attempt < retries:
                time.sleep(min(10 * attempt, 30))
    raise last_exc or RuntimeError("model call failed")


def write_task_inputs(task_dir: Path, task: dict, prompt: str) -> None:
    (task_dir / "task.json").write_text(
        json.dumps(
            {
                "id": task["id"],
                "categories": task.get("categories"),
                "input": task.get("input"),
                "expected_output_files": expected_files(task),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (task_dir / "task_prompt.txt").write_text(prompt, encoding="utf-8")


def restore_harness(task_dir: Path, task: dict, rtl_outputs: dict[str, str]) -> Path:
    harness_dir = task_dir / "harness"
    if harness_dir.exists():
        shutil.rmtree(harness_dir)
    harness_dir.mkdir(parents=True)

    for rel, content in (task.get("harness", {}).get("files", {}) or {}).items():
        dest = harness_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        content = content.replace("__OSS_SIM_IMAGE__", "nvidia/cvdp-sim:v1.0.0")
        content = content.replace("__OSS_PNR_IMAGE__", "nvidia/cvdp-sim:v1.0.0")
        dest.write_text(content, encoding="utf-8")

    for rel, content in (task.get("input", {}).get("context", {}) or {}).items():
        dest = harness_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    for rel, content in rtl_outputs.items():
        dest = harness_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    return harness_dir


def parse_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if not path.exists():
        return env
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def decode_output(data) -> str:
    if data is None:
        return ""
    if isinstance(data, str):
        return data
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return data.decode(enc)
        except Exception:
            pass
    return data.decode("utf-8", errors="replace")


def run_cmd(cmd: list[str], cwd: Path, timeout: float, env: dict | None = None) -> dict:
    start = time.time()
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(cwd),
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        stdout, _ = proc.communicate(timeout=timeout)
        output = decode_output(stdout)
        return {
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "returncode": proc.returncode,
            "elapsed_seconds": time.time() - start,
            "command": cmd,
            "output_log": output,
        }
    except subprocess.TimeoutExpired as exc:
        output = decode_output(exc.stdout)
        proc.kill()
        try:
            more_stdout, _ = proc.communicate(timeout=5)
            output += decode_output(more_stdout)
        except Exception:
            pass
        return {
            "status": "TIMEOUT",
            "elapsed_seconds": time.time() - start,
            "command": cmd,
            "output_log": output,
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "elapsed_seconds": time.time() - start,
            "command": cmd,
            "output_log": f"{type(exc).__name__}: {exc}",
        }


def run_host_harness(task_dir: Path, task: dict, rtl_outputs: dict[str, str], timeout: float) -> dict:
    harness_dir = restore_harness(task_dir, task, rtl_outputs)
    env_file = harness_dir / "src" / ".env"
    test_runner = harness_dir / "src" / "test_runner.py"
    if not env_file.exists() or not test_runner.exists():
        return {"status": "NOT_RUN", "reason": "No src/.env or src/test_runner.py in public harness."}

    env_vars = parse_env_file(env_file)
    env: dict[str, str] = {}

    def remap(value: str) -> str:
        return (
            value.replace("/code/", str(harness_dir).replace("\\", "/") + "/")
            .replace("/src/", str((harness_dir / "src")).replace("\\", "/") + "/")
            .replace("/rundir/", str((harness_dir / "rundir")).replace("\\", "/") + "/")
        )

    for key, value in env_vars.items():
        env[key] = remap(value)
    env["PYTHONPATH"] = str(harness_dir / "src")

    rundir = harness_dir / "rundir"
    rundir.mkdir(exist_ok=True)
    result = run_cmd([sys.executable, str(test_runner)], rundir, timeout, env)

    log = str(result.get("output_log") or "")
    xml_path = rundir / "sim_build" / "results.xml"
    xml_text = ""
    if xml_path.exists():
        xml_text = xml_path.read_text(encoding="utf-8", errors="ignore")
    combined = log + "\n" + xml_text
    if result.get("status") == "PASS" and (
        re.search(r'\b(?:failures|errors)="[1-9]', combined, flags=re.I)
        or re.search(r"\bFAIL(?:=|>)\s*[1-9]", combined)
    ):
        result["status"] = "FAIL"
        result["reason"] = "CVDP cocotb reported failing tests despite zero process return code."

    return result


def write_result(task_dir: Path, result: dict) -> None:
    (task_dir / "test_result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    lines = [
        f"id: {result.get('id')}",
        f"status: {result.get('status')}",
    ]
    if result.get("reason"):
        lines.append(f"reason: {result['reason']}")
    if result.get("returncode") is not None:
        lines.append(f"returncode: {result['returncode']}")
    if result.get("elapsed_seconds") is not None:
        lines.append(f"elapsed_seconds: {result['elapsed_seconds']:.2f}")
    if result.get("output_log"):
        lines.extend(["", "---- harness log ----", result["output_log"]])
    (task_dir / "test_result.txt").write_text("\n".join(lines), encoding="utf-8")


def final_result_exists(task_dir: Path) -> dict | None:
    path = task_dir / "test_result.json"
    if not path.exists():
        return None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if result.get("status") in {"PASS", "FAIL", "TIMEOUT", "MODEL_ERROR", "NOT_RUN", "ERROR"}:
        return result
    return None


def read_task_id_file(path: Path) -> list[str]:
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            ids.append(line)
    return ids


def summary_paths(out_dir: Path, task_id_file: Path | None) -> tuple[Path, Path]:
    if task_id_file:
        stem = sanitize_name(task_id_file.stem, 80)
    else:
        stem = f"pid_{os.getpid()}"
    return out_dir / f"summary_{stem}.json", out_dir / f"summary_{stem}.txt"


def write_summary(out_dir: Path, task_id_file: Path | None, summary: list[dict]) -> None:
    json_path, txt_path = summary_paths(out_dir, task_id_file)
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for item in summary:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    txt_path.write_text(
        "\n".join([f"{k}: {v}" for k, v in sorted(counts.items())]) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--task-id", action="append", default=[])
    parser.add_argument("--task-id-file", type=Path, default=None)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument("--no-harness", action="store_true")
    parser.add_argument("--model-timeout", type=float, default=180)
    parser.add_argument("--harness-timeout", type=float, default=300)
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    tasks = load_tasks(args.dataset, args.csv)
    requested = set(args.task_id)
    if args.task_id_file:
        requested.update(read_task_id_file(args.task_id_file))
    if requested:
        tasks = [task for task in tasks if task["id"] in requested]
    if args.limit is not None:
        tasks = tasks[: args.limit]
    if not tasks:
        raise RuntimeError("No tasks selected")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "README.txt").write_text(
        "CVDP cid003 direct-Verilog run through OpenRouter DeepSeek.\n"
        "Prompts are built only from public input.prompt/input.context and expected output filenames.\n"
        "Reference answers are not sent to the model.\n",
        encoding="utf-8",
    )

    client = None
    if not args.no_model:
        client = OpenAI(api_key=read_key(args.key_file), base_url=args.base_url)

    all_tasks = load_tasks(args.dataset, args.csv)
    order = {task["id"]: idx for idx, task in enumerate(all_tasks, 1)}
    summary: list[dict] = []

    for local_idx, task in enumerate(tasks, 1):
        idx = order[task["id"]]
        task_name = f"{idx:02d}_{sanitize_name(task['id'])}"
        task_dir = args.out / task_name
        task_dir.mkdir(parents=True, exist_ok=True)

        files = expected_files(task)
        prompt = build_prompt(task)
        write_task_inputs(task_dir, task, prompt)

        if args.skip_existing:
            existing = final_result_exists(task_dir)
            if existing is not None:
                item = {
                    "idx": idx,
                    "id": task["id"],
                    "status": existing.get("status"),
                    "reason": existing.get("reason"),
                    "elapsed_seconds": existing.get("elapsed_seconds"),
                }
                summary.append(item)
                write_summary(args.out, args.task_id_file, summary)
                print(f"[{local_idx}/{len(tasks)}] {task['id']} -> {item['status']} (skip)", flush=True)
                continue

        verilog_path = task_dir / "LLM_output.verilog.sv"
        meta_path = task_dir / "llm_meta.json"
        rtl_text = None
        model_error = None

        if args.no_model:
            model_error = "no_model mode enabled"
        else:
            try:
                assert client is not None
                rtl_text, meta = call_model_with_retries(
                    client,
                    args.model,
                    prompt,
                    args.model_timeout,
                    args.retries,
                    task_dir,
                )
                verilog_path.write_text(rtl_text, encoding="utf-8")
                meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception as exc:
                model_error = f"{type(exc).__name__}: {exc}"
                (task_dir / "LLM_error.txt").write_text(model_error, encoding="utf-8")

        rtl_outputs: dict[str, str] = {}
        if rtl_text is not None:
            rtl_outputs[files[0]] = rtl_text

        if model_error:
            result = {
                "id": task["id"],
                "status": "MODEL_ERROR",
                "reason": model_error,
                "expected_output_files": files,
            }
        elif args.no_harness:
            result = {
                "id": task["id"],
                "status": "NOT_RUN",
                "reason": "no_harness mode enabled",
                "expected_output_files": files,
            }
        else:
            result = run_host_harness(task_dir, task, rtl_outputs, args.harness_timeout)
            result.update({"id": task["id"], "expected_output_files": files})

        write_result(task_dir, result)
        item = {
            "idx": idx,
            "id": task["id"],
            "status": result.get("status"),
            "reason": result.get("reason"),
            "elapsed_seconds": result.get("elapsed_seconds"),
        }
        summary.append(item)
        write_summary(args.out, args.task_id_file, summary)
        print(f"[{local_idx}/{len(tasks)}] {task['id']} -> {item['status']}", flush=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
