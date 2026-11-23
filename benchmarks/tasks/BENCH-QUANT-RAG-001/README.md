# BENCH-QUANT-RAG-001 — Copias aisladas de utilidades PDF

Esta rama contiene copias **sin modificaciones** de dos scripts de `scripts/academic-rag/`. No cambiar los archivos originales ni los protocolos y resultados de los ensayos existentes.

| Script de origen | Copia independiente | SHA Git del contenido original |
| --- | --- | --- |
| `scripts/academic-rag/build_pdf_inventory.py` | `scripts/quant-rag/build_pdf_inventory.py` | `752ff3d3b7814c320a0ed3fd9593c9897d7ac283` |
| `scripts/academic-rag/extract_pdf_corpus.py` | `scripts/quant-rag/extract_pdf_corpus.py` | `4a4a9c0f956f9a056b1de0107b8274421a008cec` |

Las copias conservan inicialmente rutas, identificadores y convenciones del corpus Academic Screening. **Todavía no son una integración operativa con los dos manuales Arduino/LOGO!**. La adaptación posterior debe realizarse exclusivamente en `scripts/quant-rag/`, cambiando las rutas y la lógica específica del corpus antes de ejecutar.

Experimento previsto: 50 preguntas (20 Arduino y 30 Siemens LOGO!), seis precisiones de Qwen3-4B (FP16, Q8, Q6, Q4, Q3, Q2), tres repeticiones, condición RAG única. Los PDF serán el corpus; los cuestionarios y sus respuestas quedarán exclusivamente en evaluación.

Esta estructura se creó en la rama `feature/bench-quant-rag-001` sin modificar `main`.


## Etapa 2: índice vectorial independiente

Los resultados locales previos fueron 392 páginas y 906 chunks (900 caracteres y 150 de solapamiento). Las pruebas de segmentación fueron satisfactorias en Windows; **el índice vectorial aún debe ejecutarse y validarse localmente**.

El buscador se implementa únicamente en `scripts/quant-rag/vector_index.py`. Utiliza `intfloat/multilingual-e5-small` (SentenceTransformers, CPU por defecto), similitud coseno de vectores normalizados y prefijos E5 distintos para documentos y consultas. El índice conserva el orden de los 906 chunks. No carga respuestas de referencia.

Instalación en el Python del entorno utilizado:

```powershell
python -m pip install numpy sentence-transformers huggingface_hub
python -m unittest discover -s scripts/quant-rag/tests -v
```

Obtener una revisión exacta e inmutable del modelo de embeddings:

```powershell
$revision = python -c "from huggingface_hub import HfApi; print(HfApi().model_info('intfloat/multilingual-e5-small').sha)"
$revision
```

Crear el índice (puede descargar pesos en la primera ejecución):

```powershell
python scripts/quant-rag/vector_index.py build --chunks "C:\LocalAI-Lab-data\quant-rag\corpus\chunks.jsonl" --index-dir "C:\LocalAI-Lab-data\quant-rag\index-e5-small" --revision $revision --device cpu
```

Comprobar una consulta (el filtro de dominio es opcional y debe definirse de antemano para el protocolo final):

```powershell
python scripts/quant-rag/vector_index.py query --index-dir "C:\LocalAI-Lab-data\quant-rag\index-e5-small" --question "¿Cuáles son las funciones setup y loop en Arduino?" --domain arduino --top-k 5
```

El índice incluye `embeddings.npy` y `index_manifest.json`. El manifiesto fija el SHA de los fragmentos, SHA de la matriz vectorial, la revisión del modelo de embeddings y sus dimensiones. El buscador rechaza modificaciones inadvertidas del corpus y del índice.

**Pendiente**: fijar formalmente la política de filtro de dominio (ambos manuales vs dominio conocido); congelar los resultados Top-K de las 50 preguntas antes de la primera inferencia; medir recall@k y exactitud de páginas.
