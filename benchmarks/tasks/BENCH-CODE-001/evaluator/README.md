# BENCH-CODE-001 v1.0 — Evaluator Contract

## Hidden-evaluator policy

The exact evaluator implementation is intentionally not stored in the participant workspace.

Because LocalAI-Lab may be publicly accessible, the executable hidden-test archive should be stored separately from this repository during formal runs. Its SHA-256 must be recorded before the first formal run and reused unchanged for every v1.0 candidate.

This file documents the public evaluation contract without exposing exact assertions, fixtures or attack strings.

## Functional test families

| ID | Capability | Critical |
| --- | --- | --- |
| T01 | health endpoint and database readiness | yes |
| T02 | valid user registration | yes |
| T03 | duplicate username rejected | no |
| T04 | password is not stored in plain text and validates via login | yes |
| T05 | valid login returns usable bearer token | yes |
| T06 | invalid login rejected | yes |
| T07 | authenticated record creation | yes |
| T08 | unauthenticated record access rejected | yes |
| T09 | list returns only authenticated user's records | yes |
| T10 | owner can retrieve/update own record | yes |
| T11 | second user cannot retrieve another user's record | yes |
| T12 | second user cannot modify/delete another user's record | yes |
| T13 | owner can delete own record | yes |
| T14 | malformed/invalid payloads are rejected without server failure | no |
| T15 | data persists after application restart | yes |
| T16 | representative SQL-injection-style inputs do not bypass authentication or ownership | yes |

## Evaluator assumptions

The evaluator may:

- call the fixed API endpoints from `prompt.md`;
- create at least two users;
- inspect the benchmark MySQL database to verify password storage and referential state;
- restart the Node.js process;
- submit malformed and adversarial input values;
- verify HTTP status classes and response behavior;
- verify that ownership enforcement occurs on the server.

## Pass reporting

Report:

- tests passed / total;
- critical tests passed / total critical;
- application start PASS/FAIL;
- hidden evaluator exit status;
- unexpected server crashes;
- security/authorization failures separately.

A candidate that passes most tests but allows cross-user access must not be described as fully successful.

## Reproducibility

Before formal execution, freeze and checksum:

- evaluator source/archive;
- fixtures;
- database bootstrap;
- Node/MySQL benchmark images;
- evaluator dependencies.

Do not modify the evaluator after inspecting candidate failures without creating a new benchmark version.
