#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

CORE_FILES = [
    "backend/src/app.js",
    "backend/src/routes/admin.js",
    "backend/src/models/index.js",
    "frontend/src/admin/index.html",
    "frontend/src/admin/js/admin.js",
]


def git(ws: Path, *args: str) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(ws), *args], text=True, stderr=subprocess.STDOUT, errors="replace")
    except subprocess.CalledProcessError as e:
        return e.output or ""


def status_paths(ws: Path) -> list[str]:
    out = git(ws, "status", "--porcelain=v1")
    paths=[]
    for line in out.splitlines():
        if len(line) < 4: continue
        p=line[3:].strip()
        if " -> " in p: p=p.split(" -> ",1)[1]
        paths.append(p)
    return paths


def read_limited(path: Path, limit: int) -> str:
    try:
        txt=path.read_text(encoding="utf-8",errors="replace")
    except Exception:
        return ""
    if len(txt) <= limit: return txt
    return txt[:limit] + f"\n...[truncated at {limit} chars]...\n"


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--workspace",required=True)
    ap.add_argument("--task-prompt",required=True)
    ap.add_argument("--verifier",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--max-total-chars",type=int,default=180000)
    ap.add_argument("--max-file-chars",type=int,default=30000)
    a=ap.parse_args()
    ws=Path(a.workspace).resolve(); out=Path(a.out).resolve()
    task=Path(a.task_prompt).read_text(encoding="utf-8",errors="replace")
    verifier=Path(a.verifier).read_text(encoding="utf-8",errors="replace")
    diff=git(ws,"diff","--no-ext-diff","--unified=3")
    stat=git(ws,"diff","--stat")
    status=git(ws,"status","--short")
    paths=[]
    for p in CORE_FILES + status_paths(ws):
        if p not in paths and not any(x in p.lower() for x in ("node_modules/","package-lock.json",".png",".jpg",".jpeg",".gif",".ico")):
            paths.append(p)

    sections=[]
    sections.append("# BENCH-AGENT-001 critic context\n")
    sections.append("## Task contract\n"+task)
    sections.append("## Deterministic verifier report\n```json\n"+verifier+"\n```")
    sections.append("## Git status\n```text\n"+status+"\n```")
    sections.append("## Git diff stat\n```text\n"+stat+"\n```")
    # Limit diff so a pathological candidate cannot consume the entire critic context.
    diff_limit=max(20000, a.max_total_chars//2)
    if len(diff)>diff_limit: diff=diff[:diff_limit]+f"\n...[diff truncated at {diff_limit} chars]...\n"
    sections.append("## Candidate diff\n```diff\n"+diff+"\n```")

    used=sum(len(x) for x in sections)
    file_sections=[]
    for rel in paths:
        if used >= a.max_total_chars: break
        p=ws/rel
        if not p.is_file(): continue
        txt=read_limited(p,min(a.max_file_chars,a.max_total_chars-used))
        if not txt: continue
        block=f"## Current file: {rel}\n```text\n{txt}\n```"
        file_sections.append(block); used+=len(block)
    sections.extend(file_sections)
    content="\n\n".join(sections)
    if len(content)>a.max_total_chars:
        content=content[:a.max_total_chars]+f"\n\n...[context truncated at {a.max_total_chars} chars]...\n"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(content,encoding="utf-8")
    print(json.dumps({"out":str(out),"chars":len(content),"files_included":len(file_sections)}))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
