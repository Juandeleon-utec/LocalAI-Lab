#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json
from pathlib import Path


def load(p: Path):
    try:return json.loads(p.read_text(encoding='utf-8-sig'))
    except:return {}


def score(v):
    if v is None:return ''
    return f"{v:.1f}%"


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--dev002-root',required=True)
    ap.add_argument('--agent-root',required=True)
    ap.add_argument('--runs',nargs='*',default=[])
    ap.add_argument('--out',default='strategy-comparison.csv')
    a=ap.parse_args()
    dev=Path(a.dev002_root); agent=Path(a.agent_root)
    rows=[]
    # A: frozen baseline, never rerun.
    aa=load(dev/'audit-v2'/'DEV002-CODER30-Q3.audit.json'); ar=load(dev/'runs'/'DEV002-CODER30-Q3'/'result.json')
    am=aa.get('audited',{}).get('main',{}); ai=ar.get('inference',{}).get('llama_metric_deltas',{})
    rows.append({
      'id':'A','run_id':'DEV002-CODER30-Q3','strategy':'one-shot baseline','model':ar.get('model','local/qwen3-coder'),
      'audited_main':f"{am.get('tests_passed','')}/{am.get('tests_total','')}",
      'audited_critical':f"{am.get('critical_passed','')}/{am.get('critical_total','')}",
      'critical_completion_pct':round(100*am.get('critical_passed',0)/am.get('critical_total',1),1),
      'restart':f"{aa.get('official',{}).get('restart',{}).get('tests_passed','')}/{aa.get('official',{}).get('restart',{}).get('tests_total','')}",
      'e2e':f"{aa.get('official',{}).get('e2e',{}).get('passed','')}/{aa.get('official',{}).get('e2e',{}).get('total','')}",
      'wall_seconds':ar.get('agent',{}).get('wall_seconds'),
      'llm_calls':1,
      'prompt_tokens':ai.get('llamacpp:prompt_tokens_total'),
      'output_tokens':ai.get('llamacpp:tokens_predicted_total'),
      'prompt_tok_s':ai.get('llamacpp:prompt_tokens_seconds'),
      'generation_tok_s':ai.get('llamacpp:predicted_tokens_seconds'),
    })
    run_ids=a.runs or sorted([p.name for p in (agent/'runs').iterdir() if p.is_dir()]) if (agent/'runs').exists() else []
    for rid in run_ids:
        r=load(agent/'runs'/rid/'result.json'); audit=load(agent/'runs'/rid/'audit-v2'/f'{rid}.audit.json')
        if not r:continue
        m=audit.get('audited',{}).get('main',{})
        crit_total=m.get('critical_total') or 0; crit_pass=m.get('critical_passed') or 0
        rows.append({
          'id':r.get('strategy','?'),'run_id':rid,'strategy':r.get('strategy'),'model':r.get('model'),
          'audited_main':f"{m.get('tests_passed','')}/{m.get('tests_total','')}",
          'audited_critical':f"{crit_pass}/{crit_total}" if crit_total else '',
          'critical_completion_pct':round(100*crit_pass/crit_total,1) if crit_total else '',
          'restart':f"{audit.get('official',{}).get('restart',{}).get('tests_passed','')}/{audit.get('official',{}).get('restart',{}).get('tests_total','')}",
          'e2e':f"{audit.get('official',{}).get('e2e',{}).get('passed','')}/{audit.get('official',{}).get('e2e',{}).get('total','')}",
          'wall_seconds':r.get('agent',{}).get('pipeline_wall_seconds'),
          'llm_calls':r.get('agent',{}).get('llm_calls'),
          'prompt_tokens':r.get('inference',{}).get('prompt_tokens'),
          'output_tokens':r.get('inference',{}).get('generated_tokens'),
          'prompt_tok_s':r.get('inference',{}).get('prompt_tok_s'),
          'generation_tok_s':r.get('inference',{}).get('generation_tok_s'),
        })
    fields=['id','run_id','strategy','model','audited_main','audited_critical','critical_completion_pct','restart','e2e','wall_seconds','llm_calls','prompt_tokens','output_tokens','prompt_tok_s','generation_tok_s']
    out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"{'ID':4} {'CRIT':>8} {'COMP':>8} {'WALL':>10} {'CALLS':>6} {'GEN':>9}  MODEL/RUN")
    print('-'*90)
    for x in rows:
        comp=score(x['critical_completion_pct']) if isinstance(x['critical_completion_pct'],(int,float)) else ''
        wall=f"{x['wall_seconds']:.1f}s" if isinstance(x['wall_seconds'],(int,float)) else ''
        gen=f"{x['generation_tok_s']:.2f}" if isinstance(x['generation_tok_s'],(int,float)) else ''
        print(f"{str(x['id']):4} {x['audited_critical']:>8} {comp:>8} {wall:>10} {str(x['llm_calls']):>6} {gen:>9}  {x['run_id']}")
    print('CSV:',out)

if __name__=='__main__': main()
