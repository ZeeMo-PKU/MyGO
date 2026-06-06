#!/usr/bin/env python3
"""Generate compact report artifacts for a direct-Verilog CVDP server run."""

from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import statistics
from pathlib import Path


def clean(value: object) -> str:
    if value is None:
        return ""
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def first_error(log: str) -> str:
    hits: list[str] = []
    needles = [
        "assertionerror",
        "assert ",
        " error:",
        "error(",
        "failed",
        "mismatch",
        "attributeerror",
        "calledprocesserror",
        "not a valid l-value",
        "syntax error",
    ]
    for line in (log or "").splitlines():
        low = line.lower()
        if any(needle in low for needle in needles):
            text = line.strip()
            if text and text not in hits:
                hits.append(text)
    return hits[0][:500] if hits else ""


def classify_result(result: dict, log: str) -> tuple[str, str, str]:
    if result.get("status") == "PASS":
        return "PASS", "CVDP 判题通过。", ""
    if result.get("status") == "MODEL_ERROR":
        return "MODEL_ERROR", "模型没有产生有效 direct Verilog。", clean(result.get("reason"))

    reason = clean(result.get("reason"))
    if result.get("returncode") not in (None, 0):
        if re.search(r"error\(s\) during elaboration|not a valid l-value|syntax error|iverilog", log, re.I):
            return (
                "VERILOG_COMPILE_FAIL",
                "Icarus Verilog 编译/展开失败，说明 direct 生成的 HDL 不是有效可判题实现。",
                first_error(log),
            )
        return "HARNESS_FAIL", "CVDP harness 返回非零状态，未形成通过结果。", first_error(log)

    return (
        "CVDP_FUNCTION_FAIL",
        "CVDP cocotb 功能测试失败，生成 HDL 已进入判题但行为不符合参考测试。",
        first_error(log) or reason,
    )


def load_task_metadata(csv_path: Path) -> tuple[dict[str, str], dict[str, str]]:
    difficulty: dict[str, str] = {}
    module: dict[str, str] = {}
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            difficulty[row["id"]] = row.get("difficulty", "")
            module[row["id"]] = row.get("module", "")
    return difficulty, module


def load_mygo_rows(csv_path: Path) -> dict[str, dict]:
    if not csv_path.exists():
        return {}
    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        return {row["task_id"]: row for row in csv.DictReader(f)}


def load_direct_rows(run_dir: Path, metadata_csv: Path) -> tuple[list[dict], dict]:
    difficulty, module = load_task_metadata(metadata_csv)
    rows: list[dict] = []
    sizes: list[int] = []
    times: list[float] = []
    tokens: list[int] = []

    for task_dir in sorted(run_dir.glob("[0-9][0-9]_*")):
        result_path = task_dir / "test_result.json"
        if not result_path.exists():
            continue
        result = json.loads(result_path.read_text(encoding="utf-8"))
        task_id = result["id"]
        log = result.get("output_log") or ""
        category, reason_cn, evidence = classify_result(result, log)

        verilog_path = task_dir / "LLM_output.verilog.sv"
        meta_path = task_dir / "llm_meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        usage = meta.get("usage") or {}
        verilog_bytes = verilog_path.stat().st_size if verilog_path.exists() else 0

        sizes.append(verilog_bytes)
        if meta.get("elapsed_seconds") is not None:
            times.append(float(meta["elapsed_seconds"]))
        if usage.get("total_tokens") is not None:
            tokens.append(int(usage.get("total_tokens") or 0))

        rows.append(
            {
                "index": int(task_dir.name.split("_", 1)[0]),
                "task_id": task_id,
                "difficulty": difficulty.get(task_id, ""),
                "module": module.get(task_id, ""),
                "status": result.get("status"),
                "category": category,
                "reason_cn": reason_cn,
                "evidence": evidence,
                "returncode": result.get("returncode"),
                "elapsed_seconds": result.get("elapsed_seconds"),
                "llm_elapsed_seconds": meta.get("elapsed_seconds"),
                "llm_finish_reason": meta.get("finish_reason"),
                "llm_total_tokens": usage.get("total_tokens"),
                "verilog_bytes": verilog_bytes,
                "folder": task_dir.name,
                "result_json": f"{task_dir.name}/test_result.json",
            }
        )

    rows.sort(key=lambda row: row["index"])
    if not rows:
        raise RuntimeError(f"no direct result rows found under {run_dir}")

    empty_verilog = [
        path.parent.name
        for path in run_dir.glob("[0-9][0-9]_*/LLM_output.verilog.sv")
        if not path.read_text(encoding="utf-8", errors="ignore").strip()
    ]
    summary = {
        "verilog_bytes": {
            "min": min(sizes),
            "max": max(sizes),
            "median": statistics.median(sizes),
        },
        "llm_elapsed_seconds": {
            "min": min(times),
            "max": max(times),
            "median": statistics.median(times),
        },
        "llm_total_tokens": {
            "min": min(tokens),
            "max": max(tokens),
            "median": statistics.median(tokens),
            "sum": sum(tokens),
        },
        "validity_checks": {
            "result_json_files": len(list(run_dir.glob("[0-9][0-9]_*/test_result.json"))),
            "verilog_files": len(list(run_dir.glob("[0-9][0-9]_*/LLM_output.verilog.sv"))),
            "empty_verilog_files": empty_verilog,
        },
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_comparison(rows: list[dict], mygo_rows: dict[str, dict]) -> list[dict]:
    comparison: list[dict] = []
    for row in rows:
        mygo = mygo_rows.get(row["task_id"], {})
        direct_status = row["status"]
        mygo_status = mygo.get("status", "UNKNOWN")
        if direct_status == "PASS" and mygo_status == "PASS":
            transition = "both_pass"
        elif direct_status != "PASS" and mygo_status == "PASS":
            transition = "mygo_improved"
        elif direct_status == "PASS" and mygo_status != "PASS":
            transition = "direct_only"
        else:
            transition = "both_failed"
        comparison.append(
            {
                "index": row["index"],
                "task_id": row["task_id"],
                "difficulty": row["difficulty"],
                "direct_status": direct_status,
                "direct_category": row["category"],
                "direct_evidence": row["evidence"],
                "mygo_status": mygo_status,
                "mygo_category": mygo.get("category", ""),
                "mygo_reason": mygo.get("reason", ""),
                "transition": transition,
            }
        )
    return comparison


def write_markdown(
    path: Path,
    rows: list[dict],
    summary: dict,
    mygo_rows: dict[str, dict],
    comparison: list[dict],
) -> None:
    counts = collections.Counter(row["status"] for row in rows)
    trans_counts = collections.Counter(row["transition"] for row in comparison)
    mygo_pass = sum(1 for row in mygo_rows.values() if row.get("status") == "PASS")
    total = len(rows)
    fail_rows = [row for row in rows if row["status"] != "PASS"]

    lines: list[str] = [
        "# DeepSeek V4 direct Verilog CVDP server rerun, 2026-06-06",
        "",
        "This directory records a fresh from-scratch server rerun of the CVDP `cid003` benchmark without MyGo.",
        "",
        "## Setup",
        "",
        "- Model: `deepseek/deepseek-v4-pro` via OpenRouter",
        "- Flow: DeepSeek -> direct SystemVerilog -> Icarus/CVDP cocotb",
        "- Server: `Trifoliate`, `/home/rongxv`",
        "- Dataset: CVDP v1.1.0 non-agentic code generation, public no-commercial `cid003` subset",
        "- Execution: fresh 78-task run, 4 shards; invalid empty model outputs were rerun with a non-empty RTL guard",
        "",
        "## Result",
        "",
        f"- Total: {total}",
        f"- PASS: {counts.get('PASS', 0)}",
        f"- FAIL: {counts.get('FAIL', 0)}",
        f"- MODEL_ERROR: {counts.get('MODEL_ERROR', 0)}",
        f"- Pass rate: {counts.get('PASS', 0) / total * 100:.2f}%",
        f"- Empty Verilog outputs after rerun: {len(summary['validity_checks']['empty_verilog_files'])}",
        "",
        "`FAIL` means direct-generated SystemVerilog reached the CVDP host harness but did not produce a passing result. Some FAIL cases are functional assertion failures, while others are Icarus/SystemVerilog compile or elaboration failures.",
        "",
        "## Compared With MyGo Server Run",
        "",
        "| Metric | Direct Verilog | MyGo route |",
        "| --- | ---: | ---: |",
        f"| PASS / 78 | {counts.get('PASS', 0)} | {mygo_pass} |",
        f"| Pass rate | {counts.get('PASS', 0) / total * 100:.2f}% | {mygo_pass / 78 * 100:.2f}% |",
        "",
    ]

    if mygo_rows:
        labels = {
            "both_pass": "Both direct and MyGo pass",
            "mygo_improved": "Direct fails, MyGo passes",
            "direct_only": "Direct passes, MyGo does not pass",
            "both_failed": "Neither route passes",
        }
        lines += [
            "| Transition | Count | Meaning |",
            "| --- | ---: | --- |",
        ]
        for key in ["both_pass", "mygo_improved", "direct_only", "both_failed"]:
            lines.append(f"| {key} | {trans_counts.get(key, 0)} | {labels[key]} |")
        lines.append("")

    lines += [
        "## Failed Tasks",
        "",
        "| # | Task | Category | Evidence |",
        "| ---: | --- | --- | --- |",
    ]
    for row in fail_rows:
        evidence = clean(row["evidence"]) or clean(row["reason_cn"])
        if len(evidence) > 160:
            evidence = evidence[:157] + "..."
        lines.append(f"| {row['index']} | `{row['task_id']}` | {row['category']} | {evidence} |")

    lines += [
        "",
        "## Files",
        "",
        "- `direct_server_summary.md`: this human-readable report.",
        "- `direct_server_summary.csv`: per-task direct run table.",
        "- `direct_server_summary.json`: structured summary and rows.",
        "- `direct_vs_mygo_server_detailed.csv`: per-task comparison against the MyGo server run.",
        "- `direct_server_summary.txt`: compact status counts.",
        "",
        "API keys, raw model responses, and temporary CVDP harness work directories are intentionally not included.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--metadata-csv", type=Path, required=True)
    parser.add_argument("--mygo-summary-csv", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    rows, detail_summary = load_direct_rows(args.run_dir, args.metadata_csv)
    mygo_rows = load_mygo_rows(args.mygo_summary_csv)
    comparison = build_comparison(rows, mygo_rows)

    counts = collections.Counter(row["status"] for row in rows)
    cat_counts = collections.Counter(row["category"] for row in rows)
    summary = {
        "run_id": "deepseek-v4-direct-server-fresh-20260606",
        "date": "2026-06-06",
        "server": "Trifoliate /home/rongxv",
        "dataset": "CVDP v1.1.0 non-agentic code generation, public no-commercial cid003 subset",
        "model": "deepseek/deepseek-v4-pro",
        "flow": "DeepSeek V4 Pro -> direct SystemVerilog -> Icarus/CVDP cocotb",
        "parallelism": "4 shards from scratch; 5 empty-response cases rerun after adding non-empty RTL guard",
        "total": len(rows),
        "counts": dict(counts),
        "category_counts": dict(cat_counts),
        "pass_rate": counts.get("PASS", 0) / len(rows),
        **detail_summary,
    }

    (args.out / "direct_server_summary.json").write_text(
        json.dumps({"summary": summary, "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_csv(args.out / "direct_server_summary.csv", rows)
    write_csv(args.out / "direct_vs_mygo_server_detailed.csv", comparison)
    (args.out / "direct_server_summary.txt").write_text(
        "\n".join(
            [
                "DeepSeek V4 direct Verilog CVDP server rerun, 2026-06-06",
                f"Total: {len(rows)}",
                f"PASS: {counts.get('PASS', 0)}",
                f"FAIL: {counts.get('FAIL', 0)}",
                f"MODEL_ERROR: {counts.get('MODEL_ERROR', 0)}",
                f"Pass rate: {counts.get('PASS', 0) / len(rows) * 100:.2f}%",
                f"Empty Verilog outputs after rerun: {len(summary['validity_checks']['empty_verilog_files'])}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_markdown(args.out / "direct_server_summary.md", rows, summary, mygo_rows, comparison)
    (args.out / "README.md").write_text(
        (args.out / "direct_server_summary.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
