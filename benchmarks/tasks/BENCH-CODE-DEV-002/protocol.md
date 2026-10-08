# BENCH-CODE-DEV-002 protocol

## Purpose

Measure autonomous software-development performance on an existing codebase under a fixed repository state, prompt, context budget and external evaluator.

## Fixed inputs

- seed commit: `d429be34cab51ae58b5237ef6e0c296e2c5b67f0`
- seed SHA-256: `df80c1d7186342dead10fba07fa25d018eea56c5e49652421928868351995d55`
- prompt SHA-256: `3c44852d92d34278171e3a04ae76b208946cb7bd15ff39b2ce3f37477a9cf18f`
- benchmark freeze: v1.8
- local context budget: 49,152 tokens
- temperature: 0.1 for the tested local profiles
- one OpenCode invocation per valid run
- zero corrective human interventions

## Functional contract

The candidate must add vehicle management linked to an existing transporter, including MySQL persistence, unique registration (`matricula`), protected CRUD endpoints, validation behavior, frontend create/edit/delete flows, stable `data-testid` selectors and persistence after restart.

## Evidence

Each run preserves, when available:

- `result.json`;
- evaluator outputs;
- restart evaluator;
- Playwright E2E output;
- Git status/diff statistics;
- llama.cpp metrics snapshots;
- model metadata/health snapshots;
- startup/migration error evidence.

## Failure attribution

`INVALID_INFRA` is reserved for infrastructure failures that prevent a valid model attempt. Candidate-generated code that prevents migration/startup is scored as a candidate failure. Post-agent harness failures are recoverable without rerunning inference when the candidate state and raw evidence are preserved.

## Semantic Audit v2

The initial evaluator had negative tests that could be satisfied by a generic route-level 404. Semantic Audit v2 therefore requires evidence that the corresponding positive route/functionality exists before crediting negative-path behavior. Official scores remain immutable; audited scores are an additional analysis layer.

Auditor SHA-256:

`E26D669651FC09AD8A4E128333D7F4427DD35A91A5760E17C1AE52A21135652C`

## Interpretation limits

This benchmark is one task on one hardware/software configuration. It supports statements of the form “under BENCH-CODE-DEV-002 and this configuration,” not universal claims about model families or quantizations.
