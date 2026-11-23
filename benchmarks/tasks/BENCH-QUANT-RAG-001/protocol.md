# BENCH-QUANT-RAG-001 — Protocolo preliminar v0.1

## Pregunta de investigación
¿Cuánto cambia la calidad de respuesta de un LLM con RAG al cuantizar los mismos pesos de FP16 a Q8_0, Q6_K, Q4_K_M, Q3_K_M y Q2_K?

## Entradas congeladas
- Modelo base candidato: Qwen3-4B-Instruct-2507 (confirmar revisión y archivo exactos antes de descargar o cuantizar).
- Corpus de recuperación: exclusivamente `Manual+Programacion+Arduino.pdf` (70 páginas) y `Logo_s.pdf` (322 páginas).
- Ground truth: 20 preguntas Arduino + 30 preguntas Siemens LOGO!, con respuestas y páginas verificadas.
- **Prohibido** indexar los DOCX de preguntas/respuestas o cualquier `questions.json` en la colección RAG.
- 50 preguntas × 6 precisiones × 3 repeticiones = **900 respuestas**.
- Se excluye por ahora la condición sin RAG.

## Control experimental
1. Extraer páginas y registrar SHA-256 de cada PDF; no aplicar OCR silenciosamente.
2. Usar un modelo de embeddings fijo, un único índice y el mismo top-k por pregunta.
3. Congelar y guardar los fragmentos recuperados antes de cualquier inferencia (IDs, texto, páginas, orden y hash).
4. Usar los mismos contextos, plantilla de prompt, temperatura, semillas cuando apliquen, longitud máxima de generación, contexto y configuración de caché en las seis cuantizaciones.
5. Ejecutar una variante de modelo a la vez; verificar offload y VRAM disponible en `ia-server`.
6. Registrar por respuesta: ID pregunta, dominio, ID del contexto recuperado, ruta/hash del modelo, salida textual sin modificar, tokens, latencia, estado de finalización y errores.
7. Evaluar recuperación por página y calidad de generación por separado; mantener respuestas de referencia fuera de la entrada de inferencia.
8. Hacer comparaciones pareadas por pregunta; no tratar las tres repeticiones como preguntas independientes.

## Advertencias
- Las referencias impresas de LOGO! tienen desplazamiento de +12 respecto a la página PDF en el cuerpo principal; guardar siempre las páginas físicas del PDF como identificador canónico.
- La documentación Arduino es histórica: evaluar fidelidad al texto documental y anotar posibles discrepancias frente a implementaciones modernas.
- Ninguna cuantización se declarará 'equivalente a FP16' antes de analizar diferencias e incertidumbre.
- El rendimiento y la exactitud del experimento no están validados hasta correr las pruebas.

## Preparación de corpus
```powershell
python -m pip install pymupdf
python scripts/quant-rag/prepare_corpus.py --input-dir <directorio-manuales> --output-dir <directorio-salida>
```
Los dos ficheros producidos son `pages.jsonl` (una fila por página de PDF) y `source_inventory.json` (metadatos y hashes).
No iniciar inferencia ni embeddings antes de revisar el corpus extraído.
