import argparse,json,re,subprocess
from pathlib import Path
ap=argparse.ArgumentParser(); ap.add_argument("--run",required=True); ap.add_argument("--model",required=True); ap.add_argument("--context",type=int,required=True)
a=ap.parse_args(); run=Path(a.run); art=run/"artifacts"; ev=run/"evaluation"
def load(p):
    try:return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except:return {}
pre=load(art/"pre-run.json"); post=load(art/"post-run.json"); evaluation=load(ev/"evaluation.json"); restart=load(ev/"restart-evaluation.json")
prompt=completion=0; tool_calls=tool_errors=steps=0
p=art/"opencode-events.jsonl"
if p.exists():
    for line in p.read_text(encoding="utf-8",errors="ignore").splitlines():
        try:o=json.loads(line)
        except:continue
        steps+=1
        blob=json.dumps(o)
        # Generic usage extraction across OpenAI/OpenCode-like event shapes
        for key in ("prompt_tokens","input_tokens"):
            for m in re.finditer(rf'"{key}"\s*:\s*(\d+)',blob): prompt+=int(m.group(1))
        for key in ("completion_tokens","output_tokens"):
            for m in re.finditer(rf'"{key}"\s*:\s*(\d+)',blob): completion+=int(m.group(1))
        if re.search(r'"tool|tool_call|tool_use',blob,re.I): tool_calls+=1
        if re.search(r'"error"|tool_error|is_error',blob,re.I): tool_errors+=1
# Git stats
ws=run/"workspace"
def git(*args):
    try:return subprocess.check_output(["git","-C",str(ws),*args],text=True,stderr=subprocess.DEVNULL).strip()
    except:return ""
names=[x for x in git("diff","--name-only").splitlines() if x.strip()]
num=git("diff","--numstat")
added=deleted=0
for line in num.splitlines():
    parts=line.split("\t")
    if len(parts)>=2 and parts[0].isdigit() and parts[1].isdigit():
        added+=int(parts[0]); deleted+=int(parts[1])
# llama metrics deltas: preserve raw snapshots and extract numeric counters with token-ish names
def metrics(path):
    d={}
    if not path.exists():return d
    for line in path.read_text(errors="ignore").splitlines():
        if not line or line.startswith("#"):continue
        m=re.match(r'([A-Za-z_:][\w:]*)(?:\{[^}]*\})?\s+([-+0-9.eE]+)$',line)
        if m:
            try:d[m.group(1)]=float(m.group(2))
            except:pass
    return d
mb=metrics(art/"metrics-before.txt"); ma=metrics(art/"metrics-after.txt")
delta={k:ma[k]-mb.get(k,0) for k in ma if any(s in k.lower() for s in ("token","prompt","predicted","decode","eval"))}
result={
 "benchmark":"BENCH-CODE-DEV-002","run_id":pre.get("run_id"),"model":a.model,"context_tokens":a.context,
 "functional":{"main":evaluation,"restart":restart},
 "agent":{"wall_seconds":post.get("agent_wall_seconds"),"exit_code":post.get("agent_exit_code"),
          "event_lines":steps,"tool_event_lines":tool_calls,"error_event_lines":tool_errors,
          "files_modified":len(names),"lines_added":added,"lines_deleted":deleted},
 "inference":{"prompt_tokens_event_sum":prompt,"completion_tokens_event_sum":completion,
              "total_tokens_event_sum":prompt+completion,"llama_metric_deltas":delta,
              "note":"Los contadores de eventos se conservan como observados; metrics-before/after son la fuente cruda para auditoría."},
 "integrity":{"seed_sha256":pre.get("seed_sha256"),"prompt_sha256":pre.get("prompt_sha256"),
              "human_interventions":pre.get("human_interventions")}
}
(run/"result.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf8")
print(json.dumps({"run_id":result["run_id"],"model":a.model,"wall_seconds":result["agent"]["wall_seconds"],
                  "tests":f'{evaluation.get("tests_passed","?")}/{evaluation.get("tests_total","?")}',
                  "critical":f'{evaluation.get("critical_passed","?")}/{evaluation.get("critical_total","?")}'},ensure_ascii=False))
