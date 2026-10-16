# Gemma 4 Q3_K_M Thinking ON — inicio y contexto ampliado

**Objetivo:** servidor Linux (RX 9060 XT 16 GB, ROCm 10.0) preparado para una competencia futura con Qwen3-Coder, preservando el perfil Q3 ON del benchmark. Estas configuraciones de contexto ampliado **no han sido medidas** y no sustituyen el perfil formal 32768.

## Rutas conocidas

- Servidor: `192.168.2.237`, HTTP puerto `8088`.
- Script original: `/srv/data/benchmarks/GEMMA4-LAB-001/serve_gemma.sh`.
- Binario ROCm: `/home/jpdeleon/llama.cpp-gemma4-lab/build-rocm/bin/llama-server`.
- Modelo: `/srv/models/coding/gemma-4-26b-a4b/gemma-4-26B-A4B-it-UD-Q3_K_M.gguf`.
- Qwen habitual en `8080`, systemd/OliveTin; contexto reportado `114688`, `--fit on --fit-target 1024`. No sobrescribir la unidad de Qwen.

## Inicio conocido (32768)

```bash
cd /srv/data/benchmarks/GEMMA4-LAB-001
./serve_gemma.sh q3_on
```

Verificar desde otro terminal: `curl -sS http://192.168.2.237:8088/health` y `curl -sS http://192.168.2.237:8088/v1/models`. Confirmar `gemma4-q3_on`. Detener antes el proceso Gemma anterior con Ctrl+C en su terminal. Comprobar uso de GPU y disponibilidad antes de iniciar modelos simultáneos.

## Contexto ampliado: ejecutar una instancia experimental separada

Recomendamos probar 65536; luego 98304 y solo después 114688, midiendo memoria, tokens reales y velocidad. Sin editar el script original, ejecutar **en primer plano** esta variante con puerto 8088 disponible:

```bash
BIN=/home/jpdeleon/llama.cpp-gemma4-lab/build-rocm/bin/llama-server
MODEL=/srv/models/coding/gemma-4-26b-a4b/gemma-4-26B-A4B-it-UD-Q3_K_M.gguf
CTX=65536
"$BIN" -m "$MODEL" --alias gemma4-q3-on-long --host 0.0.0.0 --port 8088 \
  -c "$CTX" --jinja --reasoning on --fit on --fit-target 1024 \
  --metrics
```

**Importante:** esta es una configuración experimental mínima, **no** una reproducción exacta de todas las opciones del script histórico. Antes de adoptarla, revisar `serve_gemma.sh` y migrar los parámetros probados (offload, flash attention, sampling, hilos, cache KV, etc.) sin adivinar. `--fit on` puede recortar el contexto solicitado para ajustarse a memoria; verificar el contexto realmente asignado en logs del servidor y no tomar `-c` como garantía. Un modelo con 256K de contexto teórico no implica 256K disponibles en 16GB VRAM.

Consulta de argumentos del binario:

```bash
"$BIN" --help | grep -E 'ctx-size|reasoning|fit|flash-attn|cache-type|parallel'
```

Revisar slot/contexto efectivo y respuesta:

```bash
curl -sS http://192.168.2.237:8088/health
curl -sS http://192.168.2.237:8088/v1/models
curl -sS http://192.168.2.237:8088/slots
```

El endpoint `/slots` puede no estar habilitado; en ese caso usar logs de arranque. Para una prueba de contexto real, enviar una conversación progresivamente más extensa y verificar el uso sin truncamiento, el rendimiento y posibles errores de asignación.

## OpenCode

En la máquina Windows, mantener la instalación de OpenCode ya verificada o instalar la versión de la nueva prueba con protocolo explícito. El servidor informa `gemma4-q3-on-long`; definir en la configuración de OpenCode el modelo `local/gemma4-q3-on-long`, endpoint `http://192.168.2.237:8088/v1` y límite de contexto igual al **efectivo**, reservando salida (por ejemplo 8192). La estructura exacta de JSON debe copiarse del archivo OpenCode operativo: localizar `$ConfigPath` dentro de `launch-q3_on.ps1`, copiar el archivo y actualizar solo alias/contexto/ruta de API; no editar el JSON congelado ni el lanzador del benchmark.

**No exceder el contexto real del servidor en la configuración del cliente.** Contexto 114688 de Qwen y un contexto mayor realmente servido por Gemma son condiciones de infraestructura que deben informarse en cualquier comparación; para igualdad estricta, usar el mismo límite efectivo de contexto por candidato.

## Competencia futura de aplicación serenos

Comparar dos clones independientes del mismo repositorio inicial, uno por agente/modelo. Congelar prompt, requisitos de NFC/sereno, puntos obligatorios y rondas offline con SQLite/sincronización, horarios, desvíos, alertas y backend MySQL, y definir pruebas funcionales y de seguridad de antemano. No permitir intervención humana durante cada intento formal; registrar duración, pruebas, cambios, errores, consumo de tokens, versiones e incidencias. No mezclar los resultados con BENCH-CODE-001.
