#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return {}


def metrics(path: Path) -> dict[str, float]:
    d: dict[str, float] = {}
    if not path.exists(): return d
    for line in path.read_text(encoding="utf-8-sig",errors="ignore").splitlines():
        if not line or line.startswith("#"): continue
        m=re.match(r'([A-Za-z_:][\w:]*)(?:\{[^}]*\})?\s+([-+0-9.eE]+)$',line)
        if m:
            try: d[m.group(1)]=float(m.group(2))
            except ValueError: pass
    return d


def phase_delta(phase: Path) -> dict[str,float]:
    b=metrics(phase/"metrics-before.txt"); a=metrics(phase/"metrics-after.txt")
    keys=("llamacpp:prompt_tokens_total","llamacpp:prompt_tokens_cached_total","llamacpp:prompt_seconds_total",
          "llamacpp:tokens_predicted_total","llamacpp:tokens_predicted_seconds_total","llamacpp:n_decode_total")
    out={k:a.get(k,0)-b.get(k,0) for k in keys}
    # n_tokens_max is a gauge/counter-like maximum: use after snapshot value, not a delta.
    out["llamacpp:n_tokens_max"]=a.get("llamacpp:n_tokens_max",0)
    return out


def git(ws: Path,*args:str)->str:
    try:return subprocess.check_output(["git","-C",str(ws),*args],text=True,stderr=subprocess.DEVNULL,errors="replace").strip()
    except Exception:return ""


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--run",required=True); ap.add_argument("--model",required=True); ap.add_argument("--strategy",required=True); ap.add_argument("--context",type=int,required=True)
    a=ap.parse_args(); run=Path(a.run).resolve(); art=run/"artifacts"; ev=run/"evaluation"; ws=run/"workspace"
    main_eval=load(ev/"evaluation.json"); restart=load(ev/"restart-evaluation.json"); e2e=load(ev/"e2e.json")
    pre=load(art/"pre-run.json"); post=load(art/"post-run.json")
    phases=[]; totals={k:0.0 for k in ("prompt_tokens","cached_prompt_tokens","prompt_seconds","generated_tokens","predicted_seconds","n_decode")}; max_ctx=0.0
    phase_root=art/"phases"
    if phase_root.exists():
        for p in sorted(x for x in phase_root.iterdir() if x.is_dir()):
            meta=load(p/"phase.json"); d=phase_delta(p)
            item={"name":p.name,"wall_seconds":meta.get("wall_seconds"),"exit_code":meta.get("exit_code"),"metrics":d}
            phases.append(item)
            totals["prompt_tokens"]+=d["llamacpp:prompt_tokens_total"]
            totals["cached_prompt_tokens"]+=d["llamacpp:prompt_tokens_cached_total"]
            totals["prompt_seconds"]+=d["llamacpp:prompt_seconds_total"]
            totals["generated_tokens"]+=d["llamacpp:tokens_predicted_total"]
            totals["predicted_seconds"]+=d["llamacpp:tokens_predicted_seconds_total"]
            totals["n_decode"]+=d["llamacpp:n_decode_total"]
            max_ctx=max(max_ctx,d["llamacpp:n_tokens_max"])
    llm_wall=sum(float(x.get("wall_seconds") or 0) for x in phases)
    prompt_rate=(totals["prompt_tokens"]/totals["prompt_seconds"]) if totals["prompt_seconds"]>0 else None
    gen_rate=(totals["generated_tokens"]/totals["predicted_seconds"]) if totals["predicted_seconds"]>0 else None
    files=[x for x in git(ws,"status","--short").splitlines() if x.strip()]
    added=deleted=0
    for line in git(ws,"diff","--numstat").splitlines():
        p=line.split("\t")
        if len(p)>=2 and p[0].isdigit() and p[1].isdigit(): added+=int(p[0]); deleted+=int(p[1])
    ver1=load(art/"verifier-1.json"); ver2=load(art/"verifier-2.json")
    result={
      "benchmark":"BENCH-AGENT-001","task_benchmark":"BENCH-CODE-DEV-002-v1.8","run_id":pre.get("run_id"),"strategy":a.strategy,"model":a.model,"context_tokens":a.context,
      "functional":{"main":main_eval,"restart":restart,"e2e":e2e},
      "agent":{"llm_calls":len(phases),"llm_wall_seconds":round(llm_wall,3),"pipeline_wall_seconds":post.get("pipeline_wall_seconds"),"files_modified":len(files),"lines_added":added,"lines_deleted":deleted,"phases":phases},
      "verification":{"before_repair":ver1,"after_repair":ver2 or ver1},
      "inference":{"prompt_tokens":round(totals["prompt_tokens"]),"cached_prompt_tokens":round(totals["cached_prompt_tokens"]),"generated_tokens":round(totals["generated_tokens"]),"prompt_seconds":round(totals["prompt_seconds"],6),"predicted_seconds":round(totals["predicted_seconds"],6),"prompt_tok_s":round(prompt_rate,4) if prompt_rate else None,"generation_tok_s":round(gen_rate,4) if gen_rate else None,"n_tokens_max":round(max_ctx)},
      "integrity":{"seed_sha256":pre.get("seed_sha256"),"task_prompt_sha256":pre.get("task_prompt_sha256"),"dev002_freeze_sha256":pre.get("dev002_freeze_sha256"),"human_interventions":0}
    }
    (run/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"run_id":result["run_id"],"strategy":a.strategy,"llm_calls":len(phases),"pipeline_wall_seconds":post.get("pipeline_wall_seconds"),"main":f'{main_eval.get("tests_passed","?")}/{main_eval.get("tests_total","?")}',"critical":f'{main_eval.get("critical_passed","?")}/{main_eval.get("critical_total","?")}',"prompt_tok_s":result["inference"]["prompt_tok_s"],"generation_tok_s":result["inference"]["generation_tok_s"]},ensure_ascii=False))
    return 0

if __name__=="__main__": raise SystemExit(main())
