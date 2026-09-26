# BENCH-CODE-001 Harness Validation Status — 2026-09-26

## Completed

Static/offline validation completed before staging execution:

- reference-candidate `package.json` parses successfully;
- all reference-candidate JavaScript files pass `node --check`;
- hidden evaluator passes Python bytecode compilation;
- evaluation aggregator validated with synthetic pre/post evaluator results;
- evaluator invocation contract aligned with the public runner;
- custom `MYSQL_ROOT_PASSWORD` is propagated consistently to MySQL and evaluator;
- runner now requires an evaluator by default for scored execution;
- candidate Git commit, environment snapshot/hash and wall time are captured automatically;
- pre/post evaluator results are aggregated into `evaluation.json`.

## External artifacts

Hidden evaluator ZIP SHA-256:

```text
edb663ba732cd54ad3ce6cae34e73d1a351ed8afe4bcf58209dd60e46aede670
```

Reference candidate ZIP SHA-256:

```text
452d8deae6fa04b83b1356850db265105e5fa5ee94bfa4471deff5dc93d3d5cf
```

## Pending

A true end-to-end validation still requires a staging environment with Docker/MySQL.

Required next validation:

```text
preflight
-> clean MySQL start
-> reference candidate install
-> db:init
-> npm start
-> /health
-> hidden evaluator pre-restart
-> application restart without DB reset
-> hidden evaluator post-restart
-> aggregate 16/16 tests and 14/14 critical tests
```

The environment used to prepare this static validation did not provide Docker, so no MySQL PASS result is claimed here.

## Gate

Do not execute C001-A01 until the reference candidate reaches:

- 16/16 total tests;
- 14/14 critical tests;
- successful restart/persistence validation;

on the staging host selected for the benchmark.
