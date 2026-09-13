# Academic Screening Evaluation

- Papers evaluated: **24**
- Exact 4-class accuracy: **0.542**
- Macro F1: **0.408**
- Relevance-class MAE: **0.458**
- Quadratic weighted kappa: **0.488**

## Screening metrics (relevant = class >= 2)

- Recall / relevant-paper retention: **1.000**
- Precision: **0.864**
- F1: **0.927**
- False-negative rate: **0.000**
- Highly relevant (class 3) recall: **0.500**

## Reading workload

Active reading is defined as READ_FULL or READ_SECTIONS.

- Ground-truth active-reading papers: **19**
- Model active-reading papers: **22**
- Model active-reading fraction: **0.917**
- Potential active-reading reduction: **0.083**
- Relevant papers retained among active-reading recommendations: **19/19** (1.000)

## Ground-truth caveat

Interpret metrics in light of the provenance of the frozen ground truth. If labels were produced with AI assistance and human supervision, report that explicitly rather than describing them as purely human labels.

## Confusion matrix

Rows are ground truth; columns are predictions.

| GT \ Pred | 0 | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| 0 (NOT_RELEVANT) | 0 | 0 | 0 | 0 |
| 1 (TANGENTIAL) | 0 | 2 | 3 | 0 |
| 2 (RELEVANT) | 0 | 0 | 7 | 4 |
| 3 (HIGHLY_RELEVANT) | 0 | 0 | 4 | 4 |
