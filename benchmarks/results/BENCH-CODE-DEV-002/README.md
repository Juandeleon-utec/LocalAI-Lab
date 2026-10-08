# BENCH-CODE-DEV-002 results

Existing-code feature-development benchmark: add administrative vehicle management to a Node.js/Express/MySQL application in one autonomous agent pass.

## Consolidated results

| Model | Official main | Audited main | Audited critical | Critical completion | Restart | E2E | Wall s | Prompt tokens | Output tokens | Prompt tok/s | Gen tok/s | Classification |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen3-Coder-Next ~80B-A3B Q3_K_M | 15/18 | **12/18** | **10/15** | **66.7%** | **2/2** | 0/6 | 737.994 | 78,847 | 12,178 | 277.218 | 30.0023 | FAIL |
| Qwen3-Coder-30B-A3B Q3_K_M | 14/18 | **12/18** | **10/15** | **66.7%** | 1/2 | **1/6** | **535.188** | **55,204** | 13,947 | **656.087** | 36.2531 | FAIL |
| Qwen3-Coder-30B-A3B Q4_K_M | — | — | — | **N/A (startup)** | — | — | 843.555 | 87,192 | 19,903 | 611.408 | 30.7436 | **FAIL_STARTUP** |
| Qwen3.6-35B-A3B Q4_K_M | 11/18 | **5/18** | **5/15** | **33.3%** | 1/2 | 0/6 | 987.068 | 131,222 | 29,255 | 628.782 | **40.6422** | FAIL |

## Main findings

### Qwen3-Coder-Next ~80B Q3

Best persistence evidence (`2/2` restart) and the most complete backend behavior. Its main remaining backend defects were missing GET-by-id and incorrect duplicate-registration error mapping. The frontend did not satisfy the required E2E test-id contract.

### Qwen3-Coder-30B Q3

Tied Coder-Next on audited API quality (`12/18`, `10/15` critical) while completing about 27.5% faster in wall time. It also used about 30% fewer prompt tokens and was the only run to pass one E2E test. Its vehicle listing was broken and GET-by-id was absent, making restart persistence inconclusive rather than disproven.

Under this benchmark, this profile provides the strongest quality/efficiency trade-off of the tested local candidates.

### Qwen3-Coder-30B Q4

The agent completed with exit code 0, but the delivered candidate failed `db:migrate` because Sequelize registered the alias `transportista` twice. The application therefore never reached backend startup. This is classified as `FAIL_STARTUP`, attributable to candidate code rather than the harness.

The Q4 run took about 58% longer than the 30B Q3 run while producing a non-starting candidate. This result is task/configuration-specific and must not be generalized as a universal Q3-over-Q4 claim.

### Qwen3.6-35B Q4

The successful R2 run completed without a context overflow, but all positive vehicle CRUD routes returned generic 404 responses. The model created vehicle-related backend files but failed to integrate them into the router used by the application. Semantic Audit v2 reduces the misleading official `11/18` to `5/18`.

The first attempt is retained separately as a documented context-overflow attempt; R2 is the completed run used in the table.

## Why audited scores differ from official scores

The original evaluator credited some expected-error tests whenever the response was 4xx/404. If `/api/admin/vehicles` was not mounted at all, a generic `404 Ruta no encontrada` could therefore look like a correct duplicate-matricula rejection, invalid-transporter rejection, or missing-resource response.

Semantic Audit v2 removes these vacuous passes while preserving the official results unchanged.

Auditor SHA-256:

`E26D669651FC09AD8A4E128333D7F4427DD35A91A5760E17C1AE52A21135652C`

## Interpretation

The **Critical completion** percentage is calculated as audited critical tests passed / 15. It is not shown for the startup-failure run because the functional evaluator could not execute.

Two separate conclusions emerge:

- **Best backend/persistence evidence:** Qwen3-Coder-Next ~80B Q3.
- **Best quality/efficiency trade-off:** Qwen3-Coder-30B Q3.

Generation tok/s alone was not predictive of task success: Qwen3.6-35B Q4 had the highest instantaneous generation rate but the weakest completed functional result.

## Next controlled comparison

Run `Qwen3-30B-A3B-Instruct-2507 Q3_K_M` under the same benchmark as a same-scale general-instruction control against the specialized Qwen3-Coder-30B Q3 profile.
