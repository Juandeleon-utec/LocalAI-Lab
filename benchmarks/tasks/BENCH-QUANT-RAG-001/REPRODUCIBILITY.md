# BENCH-QUANT-RAG-001 — Propuesta y trazabilidad experimental

## Propuesta académica

Archivo LaTeX: [propuesta/propuesta_llm.tex](propuesta/propuesta_llm.tex).

Para compilar (desde la carpeta propuesta): pdflatex -interaction=nonstopmode -halt-on-error propuesta_llm.tex

**Pendiente:** completar segundo integrante (mínimo 2, máximo 3). Los resultados de inferencia aún no son resultados del benchmark.

## Registro reproducible

Los datos originales, documentos PDF, pesos GGUF y banco privado de respuestas permanecen en /srv/data/quant-rag/ y no se suben a Git. La rama feature/bench-quant-rag-001 conserva propuesta, protocolo y scripts. Respaldar el árbol local y el directorio de registros en un segundo medio seguro; los hashes por sí mismos no respaldan los archivos.

Ejecutar desde ~/LocalAI-Lab:

    python scripts/quant-rag/register_experiment.py

El script verifica los seis hashes observados de los GGUF, calcula hashes de los PDF, corpus, índices, dataset y resultados de recuperación, y escribe en /srv/data/quant-rag/records-v1/:

| Planilla o archivo | Contenido |
| --- | --- |
| artifacts.csv | Categoría, ruta relativa, bytes y SHA-256 de documentos y artefactos |
| models.csv | Variante, tamaño exacto, SHA-256 real y esperado, coincidencia y revisión HF |
| retrieval_per_question.csv | 100 filas (2 políticas por 50 preguntas), métricas, IDs de chunks y páginas, sin respuestas gold |
| retrieval_summary.csv | Hit@5, MRR@5 y cobertura media por política y dominio |
| provenance.json | Fecha UTC, host, commit Git, revisión de modelos y configuración de RAG |
| SHA256SUMS.txt | Hashes verificables con sha256sum -c |

Validación independiente:

    cd /srv/data/quant-rag
    sha256sum -c records-v1/SHA256SUMS.txt

El script falla si falta un archivo requerido o un modelo no coincide con los SHA-256 registrados el 23/11/2026; no modifica los originales. Para conservar instantáneas históricas, copiar records-v1 a un directorio fechado antes de reejecutarlo.

## Identidad de las versiones

- Base Hugging Face: Qwen/Qwen3-4B-Instruct-2507 @ cdbee75f17c01a7cc42f958dc650907174af0554
- GGUF: unsloth/Qwen3-4B-Instruct-2507-GGUF @ a06e946bb6b655725eafa393f4a9745d460374c9
- llama.cpp: b96806d96061049a5b574269b049bf6241d63d46
- E5: intfloat/multilingual-e5-small @ 614241f622f53c4eeff9890bdc4f31cfecc418b3
- Corpus: 392 páginas y 906 chunks; 50 preguntas; Top-K=5 global.
- Recuperación: Hit@5 0,96; MRR@5 0,8123333333; cobertura de páginas 0,95. Casos fallidos LOGO-012 y LOGO-024.
- Plan: 6 variantes, 3 repeticiones, 900 respuestas.

## Registro previsto para inferencias

Cuando se implemente el harness se deberá producir una planilla con estas columnas:

    run_id,question_id,domain,variant,repetition,model_sha256,context_sha256,prompt_sha256,temperature,seed,max_tokens,context_size,completion_text_path,finish_reason,prompt_tokens,completion_tokens,prompt_ms,predicted_ms,wall_time_ms,baseline_vram_bytes,loaded_vram_bytes,peak_vram_bytes,error

Guardar también respuestas crudas y sus hashes. La referencia gold nunca puede entrar al prompt. Una respuesta fallida debe registrarse como error, no como texto vacío. Analizar resultados pareados por pregunta, sin tratar tres repeticiones como 150 preguntas independientes.

## Precauciones

- La inferencia funcional FP16 de 34,08 tok/s no es todavía una medición RAG formal.
- El valor inicial de VRAM (9.815.388.160 bytes) es uso total de GPU, no solo memoria atribuible al modelo.
- Usar archivos de la misma revisión Unsloth no demuestra por sí solo un procedimiento de cuantización idéntico; describir procedencia y limitaciones.

## Fase de validación de seis cuantizaciones (smoke test)

El script [smoke_qwen.py](../../../scripts/quant-rag/smoke_qwen.py) comprueba los seis GGUF por separado, utilizando llama-server con ROCm. Es **una prueba funcional anterior al benchmark RAG**, no contabiliza ninguna de las 900 respuestas. Registra en /srv/data/quant-rag/runs/SMOKE-QWEN-<fecha-UTC>/:
- smoke_results.csv: éxito/error, tiempo de carga, tokens, tiempos de generación, instantáneas de VRAM y SHA-256;
- smoke_manifest.json: variantes, parámetros y hash de la planilla;
- F16/, Q8_0/, Q6_K/, Q4_K_M/, Q3_K_M/, Q2_K/: request.json, response.json si tuvo éxito, server.log, result.json, server_command.json.

Para ejecutar tras generar el inventario (puerto 18182 debe estar libre):

    cd ~/LocalAI-Lab
    source .venv-quant-rag/bin/activate
    python scripts/quant-rag/register_experiment.py
    python scripts/quant-rag/smoke_qwen.py

Por defecto se comprueban los seis modelos; con --variants Q8_0 se valida solo Q8_0. Los archivos GGUF deben superar la verificación SHA-256 antes de cargarse. El script jamás detiene servidores ajenos y rechaza un puerto ocupado. Si un modelo falla, registra el error y continúa con los demás. El script puede tardar por las cargas secuenciales.

Las mediciones de memoria son instantáneas **de toda la GPU** (antes de cargar, después y después de inferir), no mediciones precisas del máximo VRAM del proceso. No usar esos valores como peak VRAM real en el informe sin instrumentación adicional. Un posible servidor FP16 ya iniciado en el puerto 18181 debe detenerse manualmente antes de comenzar para evitar interferencia de VRAM.

