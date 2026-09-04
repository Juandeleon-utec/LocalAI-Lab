# Academic Screening Benchmark v0.1

**Project:** LocalAI-Lab  
**Module:** Academic Reviewer / Bibliographic Screening  
**Status:** Experimental protocol — pre-execution specification  
**Version:** 0.1  
**Purpose:** Define the evaluation methodology before implementing or tuning the RAG pipeline.

---

## 1. Objective

The objective of this benchmark is to evaluate the ability of local language-model and retrieval configurations to prioritize scientific literature according to its relevance to a defined research topic.

The benchmark is designed to measure not only output quality, but also computational efficiency. A configuration that produces slightly better relevance estimates while requiring substantially more execution time, memory, energy, or inference cost must not automatically be considered superior.

The benchmark therefore evaluates two independent dimensions:

1. **Screening quality** — how accurately the system identifies and ranks relevant papers.
2. **Computational efficiency** — how much time, memory, energy, and inference effort are required to obtain that result.

The benchmark is intended to support evidence-based selection of the Academic Reviewer architecture used by LocalAI-Lab.

---

## 2. Research Questions

The benchmark should answer the following questions:

### RQ1 — Screening accuracy
How accurately can the system distinguish highly relevant, relevant, tangential, and non-relevant scientific papers?

### RQ2 — Ranking quality
Does the system place the most relevant papers near the top of the recommended reading list?

### RQ3 — Human workload reduction
How much can the system reduce the number of papers requiring manual reading while preserving high recall of relevant literature?

### RQ4 — Input depth
How much quality is gained by progressing from title only, to title + abstract, to title + abstract + keywords, and finally to full-text analysis?

### RQ5 — Retrieval architecture
Does hybrid retrieval improve screening quality compared with dense retrieval alone?

### RQ6 — Reranking
Does a reranker provide a measurable improvement after hybrid retrieval?

### RQ7 — Efficiency
How do model and pipeline choices affect wall-clock execution time, papers processed per minute, token usage, RAM, VRAM, power, and energy consumption?

### RQ8 — Quality-efficiency trade-off
Which configurations lie on the Pareto frontier when considering both screening quality and computational cost?

---

## 3. Benchmark Philosophy

### 3.1 Predefined evaluation
Evaluation criteria must be defined before model comparison begins. Metrics, relevance labels, dataset rules, and execution procedures must not be modified retrospectively to favor a particular model or architecture.

### 3.2 Reproducibility
Every benchmark execution must record sufficient information to reproduce it, including model, model revision, quantization, model hash when available, embedding model, reranker, prompt version, retrieval parameters, software versions, operating system, kernel, hardware, and inference arguments.

### 3.3 Quality and efficiency are separate outcomes
A model is not automatically considered better because it achieves the highest quality metric.

Example:

```text
Configuration A
F1 = 0.89
Execution time = 10 min
Energy = 40 Wh

Configuration B
F1 = 0.90
Execution time = 23 min
Energy = 90 Wh
```

Configuration B has higher F1, but whether the 0.01 improvement justifies more than twice the execution time and energy must be evaluated explicitly.

### 3.4 Raw measurements are preserved
Derived scores must never replace raw measurements. All benchmark runs should retain raw predictions, timing data, token counts, telemetry, model outputs, errors, and intermediate retrieval results when applicable.

### 3.5 Human judgment remains the reference
The purpose of the system is to assist literature screening, not to replace academic judgment. A manually reviewed subset of papers constitutes the reference ground truth.

---

## 4. Initial Dataset

### 4.1 Source
The initial corpus will consist primarily of scientific literature previously retrieved through Scopus.

Documents may include exported Scopus metadata, abstracts, keywords, PDFs of full papers, and supplementary bibliographic metadata.

### 4.2 Initial dataset size
The first benchmark should use approximately:

```text
30–50 papers
```

This is intended as a controlled development dataset rather than a statistically definitive corpus.

The dataset should contain a mix of clearly relevant papers, moderately relevant papers, tangential papers, and clearly irrelevant papers returned by broad searches.

A larger validation corpus may be created after the pipeline stabilizes.

### 4.3 Paper identifier
Each paper must receive a stable identifier independent of its filename.

Example:

```text
P001
P002
P003
...
```

### 4.4 Minimum metadata
Whenever available, store:

```text
paper_id
title
authors
year
doi
source
abstract
keywords
scopus_id
filename
```

Additional metadata may include journal, conference, volume, issue, pages, citation_count, document_type, and language.

---

## 5. Human Ground Truth

A manually evaluated subset will be used as the reference for model comparison. The evaluator should assign both a relevance level and a reading recommendation.

### 5.1 Relevance scale

| Score | Label | Definition |
|---:|---|---|
| 3 | Highly relevant | Directly supports the research problem, methodology, implementation, or state of the art |
| 2 | Relevant | Provides useful related evidence but is not central |
| 1 | Tangential | Has partial thematic overlap but limited direct value |
| 0 | Not relevant | Does not meaningfully contribute to the research question |

### 5.2 Reading recommendation

Each paper should also receive one operational label:

```text
READ_FULL
READ_SECTIONS
REFERENCE_ONLY
DISCARD
```

| Recommendation | Meaning |
|---|---|
| READ_FULL | Paper should receive full manual reading |
| READ_SECTIONS | Only selected sections are likely necessary |
| REFERENCE_ONLY | Useful mainly as supporting/background citation |
| DISCARD | No meaningful value for the current research objective |

### 5.3 Relevance dimensions
Where useful, relevance may also be scored independently across several dimensions, such as topic_match, methodology_match, hardware_or_sensor_match, dataset_match, edge_ai_relevance, machine_learning_method_match, experimental_design_value, and state_of_the_art_value.

These scores are secondary and should not replace the principal relevance label.

---

## 6. Screening Output Schema

Every system configuration should produce a structured record for each paper.

Example:

```json
{
  "paper_id": "P017",
  "relevance_score": 8.6,
  "relevance_class": 3,
  "decision": "READ_FULL",
  "reason": "The paper directly investigates vibration-based fault diagnosis in induction motors using embedded sensing and deep learning.",
  "key_topics": [
    "induction motor",
    "vibration analysis",
    "predictive maintenance"
  ],
  "recommended_sections": [
    "Methodology",
    "Experimental Setup",
    "Results"
  ]
}
```

The exact JSON schema may evolve before implementation, but it must remain fixed during comparative benchmark runs.

---

## 7. Benchmark Configurations

### Configuration A — Title only
Input: title.

Purpose: establish the lowest-cost baseline.

### Configuration B — Title + Abstract
Input: title + abstract.

Purpose: determine the value added by abstracts.

### Configuration C — Title + Abstract + Keywords
Input: title + abstract + keywords.

Purpose: measure whether structured author/index keywords improve screening.

### Configuration D — Full Text
Input: parsed full text.

Purpose: evaluate the benefit and cost of processing complete papers.

### Configuration E — Hybrid RAG

```text
Dense retrieval
+
Sparse / lexical retrieval
        ↓
Fusion
        ↓
LLM screening
```

Purpose: compare hybrid retrieval with simpler approaches.

### Configuration F — Hybrid RAG + Reranker

```text
Dense retrieval
+
Sparse retrieval
        ↓
Fusion
        ↓
Candidate set
        ↓
Reranker
        ↓
Top-ranked evidence
        ↓
LLM screening
```

Purpose: determine whether reranking provides sufficient quality improvement to justify its additional cost.

---

## 8. Planned RAG Architecture

```text
PDF / DOCX / Scopus metadata
              │
              ▼
      Document extraction
              │
              ▼
   Structure-aware chunking
              │
       ┌──────┴──────┐
       ▼             ▼
 Dense vectors   Sparse index
       │             │
       └──────┬──────┘
              ▼
            Qdrant
              │
       Hybrid retrieval
              │
             RRF
              │
       Top-N candidates
              │
           Reranker
              │
       Top-K evidence
              │
              ▼
       Academic LLM
              │
              ▼
 Screening decision
 + rationale + citations
```

---

## 9. Document Processing

### 9.1 Structure-aware chunking
The benchmark should avoid relying exclusively on fixed-size token chunks. Whenever feasible, the parser should preserve scholarly structure such as Title, Abstract, Introduction, Related Work, Methodology, Dataset, Experimental Setup, Results, Discussion, Conclusion, and References.

A chunk should not arbitrarily split a coherent paragraph or subsection unless necessary.

### 9.2 Chunk metadata
Each chunk should retain metadata such as:

```text
paper_id
document_title
authors
year
page
section
subsection
chunk_id
doi
source_filename
```

Example:

```text
paper_id: P017
section: Methodology
subsection: Vibration Acquisition
page: 6
chunk_id: P017-METH-004
```

This metadata is required for traceable academic citations.

---

## 10. Retrieval Evaluation

Retrieval quality must be evaluated independently from final LLM answer quality whenever ground-truth evidence is available.

### Hit Rate@K
Measures whether at least one relevant passage appears in the top K retrieved chunks.

### Recall@K
Measures how much of the known relevant evidence is retrieved.

### Precision@K
Measures how much of the top K retrieval result is relevant.

### Mean Reciprocal Rank — MRR
Measures how early the first relevant result appears.

### nDCG@K
Normalized Discounted Cumulative Gain evaluates ranking quality while accounting for graded relevance.

nDCG is particularly important for this project because the real goal is not merely identifying relevant papers, but prioritizing the most useful ones near the top of the reading list.

---

## 11. Screening Quality Metrics

### 11.1 Classification metrics

```text
Accuracy
Precision
Recall
F1-score
Macro F1
Weighted F1
```

Because the dataset may be imbalanced, Macro F1 should be reported alongside Accuracy.

### 11.2 Ordinal-score metrics

```text
Mean Absolute Error
Spearman rank correlation
Cohen's weighted kappa
```

These metrics help distinguish a one-level error from a completely incorrect classification.

### 11.3 Ranking metrics

```text
Precision@K
Recall@K
MRR
nDCG@K
```

Suggested values of K:

```text
K = 5
K = 10
K = 20
```

depending on corpus size.

---

## 12. Human Reading Reduction

One of the main practical metrics will be the reduction in human reading effort.

The benchmark should answer:

> What percentage of papers can be excluded from full manual review while preserving a predefined recall of genuinely relevant papers?

Example target:

```text
Human reading reduction = 62%
Recall of relevant papers = 96%
```

This may be expressed as:

```text
reading_reduction =
1 - papers_requiring_manual_review / total_papers
```

The metric must always be reported together with relevance recall.

A high reduction rate with poor recall is not useful.

A possible operational target for future experiments is:

```text
Recall >= 0.95
```

while maximizing reading reduction.

This threshold is a benchmark target, not a claim about current system performance.

---

## 13. Efficiency Metrics

Quality metrics must be accompanied by technical efficiency measurements.

### 13.1 Execution time

Measure:

```text
total_wall_time_s
time_per_paper_s
```

For batch processing:

```text
papers_per_minute
papers_per_hour
```

### 13.2 Pipeline timing

Where practical, separate:

```text
T_total =
T_parse
+ T_embedding
+ T_index
+ T_retrieval
+ T_reranking
+ T_llm
```

Record:

```text
parse_time_s
embedding_time_s
index_time_s
retrieval_time_s
reranking_time_s
inference_time_s
```

This allows bottleneck analysis.

### 13.3 Token usage

For each LLM request:

```text
input_tokens
output_tokens
total_tokens
```

For a benchmark run:

```text
cumulative_input_tokens
cumulative_output_tokens
tokens_per_paper
```

### 13.4 Throughput

When available:

```text
prompt_tokens_per_second
generation_tokens_per_second
```

### 13.5 Memory

Measure:

```text
peak_vram_mb
average_vram_mb
peak_ram_mb
average_ram_mb
```

### 13.6 GPU telemetry

Measure when available:

```text
gpu_utilization_percent
gpu_temperature_c
gpu_power_w
```

### 13.7 Energy

Where sampling frequency permits numerical integration:

```text
energy_wh
energy_wh_per_paper
```

Approximation:

```text
Energy (Wh) =
integral(power_W over time_seconds) / 3600
```

Peak power alone must not be reported as energy consumption.

---

## 14. Cost Metrics

### 14.1 Local operational cost

Where electricity pricing is available:

```text
local_energy_cost =
energy_kWh × electricity_price_per_kWh
```

Hardware acquisition and depreciation may be evaluated separately and should not be mixed into electricity cost without explicitly defining the accounting model.

### 14.2 Simulated cloud-equivalent cost

To enable comparison against hypothetical hosted inference, the benchmark may calculate:

```text
simulated_input_cost
simulated_output_cost
simulated_total_cost
```

using configurable price profiles.

These must always be labeled **SIMULATED CLOUD COST** and must not be represented as actual expenditure unless the external API was truly used.

---

## 15. Reliability Metrics

Record operational failures such as:

```text
parse_errors
invalid_json_outputs
model_timeouts
retrieval_failures
reranker_failures
out_of_memory_events
automatic_retries
manual_interventions
```

Also record:

```text
successful_papers
failed_papers
success_rate
```

A configuration that requires frequent manual intervention should not be considered equivalent to one that completes autonomously.

---

## 16. Pareto Analysis

No single weighted "best model score" should initially be used.

Instead, configurations should be compared using Pareto dominance.

A configuration A dominates B if A is equal or better in quality, equal or faster in execution time, and equal or lower in resource consumption, with at least one strict improvement.

Example comparison axes:

```text
F1 vs execution time
nDCG@10 vs energy
Recall@10 vs VRAM
Human reading reduction vs processing time
```

Models on the Pareto frontier represent efficient alternatives for different operational requirements.

---

## 17. Experimental Run Metadata

Every benchmark run must receive a unique identifier.

Example:

```text
ASB-0001
ASB-0002
ASB-0003
```

Each run should record:

```text
run_id
timestamp
dataset_version
ground_truth_version
configuration
prompt_version

llm_model
llm_revision
llm_quantization
llm_hash

embedding_model
embedding_revision
embedding_hash

reranker_model
reranker_revision
reranker_hash

vector_database
vector_database_version

llama_cpp_commit
rocm_version
kernel_version
os_version

cpu
gpu
gpu_architecture
ram_total_mb
vram_total_mb

context_size
batch_size
retrieval_top_n
reranker_top_k
sampling_parameters
```

---

## 18. Result Record

A benchmark result table should include at least:

```text
run_id
configuration
model
embedding_model
reranker_model
document_count

accuracy
precision
recall
f1
macro_f1
mae
spearman
mrr
ndcg_5
ndcg_10
precision_10
recall_10

reading_reduction
relevant_paper_recall

input_tokens
output_tokens
total_tokens

total_time_s
time_per_paper_s
papers_per_minute

peak_vram_mb
peak_ram_mb
average_power_w
peak_power_w
energy_wh

errors
retries
manual_interventions
```

---

## 19. Raw Data Storage

Suggested project layout:

```text
/srv/data/benchmarks/academic-rag/
├── datasets/
├── ground-truth/
├── runs/
│   ├── ASB-0001/
│   │   ├── config.json
│   │   ├── predictions.jsonl
│   │   ├── retrieval.jsonl
│   │   ├── telemetry.csv
│   │   ├── timing.json
│   │   ├── metrics.json
│   │   └── run.log
│   └── ASB-0002/
├── reports/
└── plots/
```

Repository documentation may live under:

```text
docs/academic-rag/
```

while large benchmark artifacts should remain under `/srv/data`.

---

## 20. Prompt Versioning

Prompts used for screening must be version controlled.

Example:

```text
prompts/academic-screening-v0.1.txt
prompts/academic-screening-v0.2.txt
```

A prompt change creates a new experimental condition. Results obtained with different prompt versions must not be treated as directly identical configurations.

The prompt should require structured output and discourage unsupported claims.

---

## 21. Suggested Screening Prompt Requirements

The final screening prompt should require the model to:

1. evaluate only the provided paper information;
2. assign a relevance level;
3. provide an operational reading recommendation;
4. explain its reasoning briefly;
5. identify which research dimensions are relevant;
6. avoid inferring missing experimental details;
7. return valid structured output;
8. identify insufficient evidence when only title/abstract information is available.

---

## 22. Full-Text Citation Requirements

For full-text and RAG configurations, every substantive finding should be traceable to source evidence.

Preferred citation metadata:

```text
paper_id
filename
page
section
subsection
chunk_id
```

Example output:

```text
The paper evaluates vibration-based fault detection
using an embedded sensor platform.

Source:
P017
Methodology — Sensor Acquisition
Page 6
Chunk P017-METH-004
```

The system must distinguish claims directly supported by retrieved text, model interpretation, and missing information.

---

## 23. Initial Experimental Sequence

### Phase 1 — Dataset preparation
1. Collect 30–50 papers.
2. Normalize metadata.
3. Assign stable paper IDs.
4. Create the human ground truth.
5. Freeze dataset version `v0.1`.

### Phase 2 — Non-RAG screening
Run:

```text
A — Title
B — Title + Abstract
C — Title + Abstract + Keywords
D — Full text
```

This establishes whether deeper document processing produces enough benefit to justify its computational cost.

### Phase 3 — Retrieval benchmark
Evaluate:

```text
Dense retrieval
Sparse retrieval
Hybrid retrieval
```

independently from LLM answer generation where possible.

### Phase 4 — Reranking
Compare:

```text
Hybrid
vs
Hybrid + reranker
```

### Phase 5 — End-to-end Academic Reviewer
Combine:

```text
document ingestion
+ retrieval
+ reranking
+ academic LLM
+ citations
```

and compare quality and efficiency against the earlier baselines.

---

## 24. Repetition and Variability

Because LLM generation can be stochastic, repeated runs should be considered for configurations using non-deterministic sampling.

Recommended approach:

```text
3 repeated runs per final candidate configuration
```

for timing and generation-quality analysis.

For deterministic or near-deterministic settings, repetitions are still useful for measuring runtime variability.

Report mean, standard deviation, minimum, and maximum for execution time and other variable metrics.

---

## 25. Dataset Separation

Once model and prompt tuning begins, the dataset should ideally be divided into:

```text
development set
validation/test set
```

The development set may be used to tune prompts, select retrieval parameters, choose chunk size, and choose Top-N and Top-K.

The final evaluation set should not be used for tuning.

This separation becomes mandatory before making publication-level performance claims.

---

## 26. Threats to Validity

### Human-label subjectivity
Paper relevance is partly subjective and depends on the research question.

Mitigation: document relevance criteria, preserve evaluator notes, and optionally introduce a second evaluator later.

### Dataset bias
A small corpus retrieved through one Scopus query may not represent broader literature.

Mitigation: preserve search strings, expand corpus in later benchmark versions, and report dataset composition.

### Model contamination
A model may have encountered some published papers during training. The benchmark evaluates screening behavior on the local corpus, not novelty of knowledge.

### Parsing quality
Poor PDF extraction can reduce RAG quality independently of retrieval/model performance. Parsing errors should therefore be recorded separately.

### Hardware-specific efficiency
Timing and energy results are specific to the LocalAI-Lab hardware and software configuration. Quality measurements may generalize more broadly than efficiency measurements.

---

## 27. Initial Success Criteria

Academic Screening Benchmark v0.1 is considered operational when the project can:

1. ingest the frozen benchmark corpus;
2. produce one structured screening decision per paper;
3. compare predictions with human ground truth;
4. calculate quality metrics automatically;
5. record total and per-stage execution time;
6. record token usage;
7. record RAM and VRAM;
8. record GPU telemetry;
9. estimate/integrate energy consumption where possible;
10. generate a reproducible benchmark report.

No minimum accuracy is required for the benchmark itself to be considered successfully implemented. The purpose of v0.1 is to create a reliable measurement framework.

---

## 28. Decision Rule for Architecture Selection

The final Academic Reviewer configuration should not be selected from a single metric.

Preference should be given to configurations that:

1. achieve high recall of truly relevant papers;
2. rank highly relevant literature near the top;
3. substantially reduce manual reading workload;
4. maintain acceptable execution time;
5. avoid excessive RAM/VRAM requirements;
6. use energy efficiently;
7. produce traceable and reproducible results;
8. minimize manual intervention.

If two configurations produce statistically or practically equivalent quality, the lower-cost configuration should be preferred.

---

## 29. Expected Deliverables

```text
docs/academic-rag/academic-screening-benchmark-v0.1.md

prompts/
└── academic-screening-v0.1.txt

/srv/data/benchmarks/academic-rag/
├── datasets/
├── ground-truth/
├── runs/
└── reports/
```

Potential later artifacts:

```text
academic-screening-results.csv
academic-screening-summary.md
pareto-quality-vs-time.png
pareto-quality-vs-energy.png
reading-reduction-analysis.csv
```

---

## 30. Future Extensions

After the baseline architecture is validated, future experiments may evaluate multiple embedding models, multiple rerankers, query rewriting, multi-query retrieval, hierarchical retrieval, contextual chunking, citation verification, GraphRAG, agentic RAG, automatic evidence matrices, cross-document contradiction detection, systematic-review assistance, and external bibliographic search integration.

These extensions should only be introduced after the baseline benchmark is stable.

---

## 31. Core Experimental Principle

> **A model or architecture is not better merely because it produces a higher-quality result. It is better only when the quality improvement is justified by its computational and operational cost.**

Accordingly, LocalAI-Lab will report both:

```text
QUALITY
and
EFFICIENCY
```

for every serious Academic Reviewer benchmark.

This principle should remain unchanged across future benchmark versions.
