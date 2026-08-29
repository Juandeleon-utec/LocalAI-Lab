# Academic RAG — Initial Design

## Goal

Build a local Retrieval-Augmented Generation pipeline for querying, comparing, reviewing and drafting from academic papers while preserving traceable evidence.

## Planned pipeline

```text
PDF / article collection
        |
        v
Text + metadata extraction
        |
        v
Document normalization and structure detection
        |
        +--> title / authors / DOI
        +--> abstract
        +--> sections
        +--> tables / captions where feasible
        +--> references
        |
        v
Structure-aware chunking
        |
        v
Embeddings
        |
        v
Vector database
        |
        v
Candidate retrieval
        |
        v
Reranking
        |
        v
Academic LLM
        |
        v
Answer / comparison / draft with traceable sources
```

## Initial candidate components

- Embeddings: Qwen3-Embedding family.
- Reranker: Qwen3-Reranker family.
- Vector database: to be selected by benchmark.
- Main academic LLM: to be selected by controlled evaluation.

## Source-traceability requirement

Each retrieved chunk should preserve, where available:

- document identifier;
- title;
- authors;
- DOI;
- page;
- section/subsection;
- chunk identifier;
- extraction method/version.

Answers intended for research use should distinguish model-generated synthesis from retrieved evidence.

## Evaluation priorities

The RAG system will be judged on more than fluency. Key properties include correct retrieval, evidence traceability, citation correctness, hallucination resistance, multi-paper comparison and scientific-writing usefulness.

## Future experimental variables

- chunk size and overlap;
- semantic vs structure-aware chunking;
- embedding model;
- embedding dimensionality;
- number of retrieved candidates;
- reranker model;
- final context size;
- LLM family and quantization.
