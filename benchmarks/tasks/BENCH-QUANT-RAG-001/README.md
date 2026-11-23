# BENCH-QUANT-RAG-001 — Copias aisladas de utilidades PDF

Esta rama contiene copias **sin modificaciones** de dos scripts de `scripts/academic-rag/`. No cambiar los archivos originales ni los protocolos y resultados de los ensayos existentes.

| Script de origen | Copia independiente | SHA Git del contenido original |
| --- | --- | --- |
| `scripts/academic-rag/build_pdf_inventory.py` | `scripts/quant-rag/build_pdf_inventory.py` | `752ff3d3b7814c320a0ed3fd9593c9897d7ac283` |
| `scripts/academic-rag/extract_pdf_corpus.py` | `scripts/quant-rag/extract_pdf_corpus.py` | `4a4a9c0f956f9a056b1de0107b8274421a008cec` |

Las copias conservan inicialmente rutas, identificadores y convenciones del corpus Academic Screening. **Todavía no son una integración operativa con los dos manuales Arduino/LOGO!**. La adaptación posterior debe realizarse exclusivamente en `scripts/quant-rag/`, cambiando las rutas y la lógica específica del corpus antes de ejecutar.

Experimento previsto: 50 preguntas (20 Arduino y 30 Siemens LOGO!), seis precisiones de Qwen3-4B (FP16, Q8, Q6, Q4, Q3, Q2), tres repeticiones, condición RAG única. Los PDF serán el corpus; los cuestionarios y sus respuestas quedarán exclusivamente en evaluación.

Esta estructura se creó en la rama `feature/bench-quant-rag-001` sin modificar `main`.
