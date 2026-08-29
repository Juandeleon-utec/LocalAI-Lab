# Coding Agent — Initial Design

## Goal

Provide a local coding-agent workflow comparable in spirit to modern terminal-based coding assistants while keeping model execution and project data under local control.

## Target tasks

- Python development;
- backend applications;
- mobile application development;
- repository understanding;
- bug fixing;
- refactoring;
- test generation;
- documentation;
- build/test execution.

## Candidate stack

Primary model family:

- Qwen3-Coder.

Agent frontends to evaluate:

- OpenCode;
- Qwen Code;
- Aider.

## Expected workflow

```text
User task
   |
   v
Agent
   |
   +--> inspect repository
   +--> search files
   +--> edit code
   +--> run commands
   +--> run tests/build
   +--> inspect errors
   +--> iterate
   |
   v
Final patch / completed task
```

## Experimental requirement

The complete agent system, not only the LLM, must be treated as the experimental unit when comparing against products such as Claude Code.

For each controlled task, preserve the initial repository commit, prompt, agent configuration, model, tool permissions, resulting patch, execution trace where available, test outcome, timing and resource telemetry.

## Initial comparison dimensions

- successful task completion;
- correctness/test pass rate;
- time to solution;
- number of iterations/tool calls;
- human intervention;
- code-change size;
- inference throughput;
- RAM/VRAM utilization;
- energy and cost where measurable.
