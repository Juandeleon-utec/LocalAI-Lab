# Semantic Audit v2

This audit is complementary to BENCH-CODE-DEV-002. It never overwrites official evaluator results and never reruns a model.

It removes vacuous PASS results in negative tests when a generic route-level 404 is the only reason the test passed. Positive route/functionality evidence is required before missing-resource and validation behavior can receive credit.

Auditor SHA-256:

`E26D669651FC09AD8A4E128333D7F4427DD35A91A5760E17C1AE52A21135652C`

Audited result summary:

| Run | Official | Audited | Official critical | Audited critical |
| --- | ---: | ---: | ---: | ---: |
| DEV002-CODER-NEXT-Q3 | 15/18 | 12/18 | 12/15 | 10/15 |
| DEV002-CODER30-Q3 | 14/18 | 12/18 | 11/15 | 10/15 |
| DEV002-CODER30-Q4 | — | — | — | — |
| DEV002-QWEN36-35B-Q4-R2 | 11/18 | 5/18 | 8/15 | 5/15 |
