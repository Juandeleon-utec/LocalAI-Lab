# Academic Screening A003 — Prompt Calibration Plan

## Motivation

A001 achieved perfect relevant-paper recall on Academic Screening v0.1 but over-classified many papers as `HIGHLY_RELEVANT`.

Observed A001 classification errors:

- P004: 2 -> 3
- P005: 2 -> 3
- P006: 1 -> 3
- P007: 2 -> 3
- P008: 1 -> 3
- P009: 1 -> 3
- P011: 2 -> 3
- P013: 2 -> 3
- P014: 2 -> 3
- P015: 2 -> 3
- P016: 2 -> 3
- P017: 2 -> 3
- P019: 2 -> 3
- P020: 2 -> 3

The three binary false positives were P006, P008, and P009, all ground-truth class 1 but predicted class 3.

This pattern indicates a systematic upward-calibration bias rather than random classification noise. The model appears to treat strong keyword/domain overlap as evidence of central relevance.

## A003 intervention

A003 changes only the screening prompt. Model, quantization, dataset, research objective, temperature, seed, endpoint, and evaluation protocol remain unchanged.

Prompt v0.2 introduces:

- explicit separation between keyword overlap and direct methodological contribution;
- stricter requirements for class 3;
- a preference for class 2 when uncertain between 2 and 3;
- a preference for class 1 when evidence does not demonstrate direct technical or experimental utility;
- containment rules for generic predictive maintenance, generic anomaly detection, generic AI/ML, edge, IoT, and sensor papers;
- deterministic mapping from relevance class to reading decision.

## Controlled variables

Keep fixed from A001:

- model alias: `qwen3-academic`
- model: Qwen3-30B-A3B-Instruct-2507 Q3_K_M
- dataset: Academic Screening v0.1, 24 papers
- research objective: unchanged
- temperature: 0.0
- seed: 42
- max completion tokens: 1200
- context: 8192

Change only:

- prompt: `prompts/academic-screening-v0.2.txt`
- run identifier: `A003`

## Primary success criteria

The central constraint is preservation of relevant literature.

- Relevant-paper recall should remain 1.00 on the current 19 relevant papers. One false negative would reduce recall to 18/19 = 0.947 and would miss the benchmark target of >=0.95.
- False-negative rate should remain 0.00.
- Class-3 recall should be monitored separately.

Desired improvements:

- higher relevant-paper precision;
- fewer class-1 -> class-3 errors;
- higher exact 4-class accuracy;
- higher macro F1;
- lower relevance-class MAE;
- higher quadratic weighted kappa;
- greater active-reading reduction under the deterministic policy.

## Evaluation

Run the same evaluator used for A001 against the A003 run directory, then compare A001 and A003 side by side.

A003 should not be considered an improvement if better precision or reading reduction is obtained by sacrificing relevant-paper recall below the predefined target.

## Scientific caution

The calibration rules were motivated by observed A001 errors on the same 24-paper benchmark. Therefore A003 is a development-set calibration experiment, not an unbiased external validation. Academic Screening v0.1 must remain frozen, and a later v0.2 or independent hold-out corpus should be used to test whether the calibration generalizes.
