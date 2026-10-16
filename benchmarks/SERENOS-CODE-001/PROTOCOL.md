# SERENOS-CODE-001 — Protocolo de competencia incremental Qwen vs Gemma

**Estado:** protocolo propuesto (2026-10-16), todavía sin ejecuciones. Dos agentes/implementaciones separadas de OpenCode: Qwen3-Coder-30B-A3B-Instruct Q3_K_M y Gemma 4 26B-A4B Q3_K_M Thinking ON. Baseline informativo: [BENCH-CODE-001 executive comparison](../BENCH-CODE-001/EXECUTIVE-COMPARISON.md).

## 1. Pregunta experimental

¿Cuál modelo entrega mayor porcentaje de requisitos funcionales correctos a la primera, requiere menos prompts de reparación, consume menos tiempo y tokens, e introduce menos regresiones conforme se añaden módulos a una aplicación Android de control de rondas de serenos?

Los modelos no deberán ver código, trazas privadas ni salidas del contrincante. Su interacción tiene que ser separada y atribuible.

## 2. Producto y alcance

Aplicación Android nativa para 2–10 usuarios de personal operativo, y backend propio MySQL, con modo sin conexión. Usar SQLite local para rondas y cola de sincronización; backend expuesto exclusivamente por API autenticada (no conectar Android directamente a MySQL). Identificación de sereno por tag NFC inicial/final; lecturas NFC en puntos de control; selección de recorrido; secuencia sugerida de puntos; cobertura obligatoria de puntos, registro de omisiones; cierre normal por tag Serena/o autorizado; rondas interrumpidas con estado incompleta; tiempo máximo configurable con alerta, nunca autocierre; tolerancias de localización configurables de ~20 a >100m donde corresponda; sincronización al recuperar Wi-Fi, con idempotencia. Geocercas GPS para asistencia de tercerizados constituye **otro módulo**, posterior a serenos, y no debe mezclarse sin aprobar el núcleo.

Hardware Android objetivo: terminal industrial compatible con NFC y GPS, modelo/version Android exacta y API NFC deben confirmarse con dispositivo real antes de fijar requisitos. HH65 es una opción conocida en evaluación, **no validada aquí**. Prototipo se puede probar con teléfono Android NFC y etiquetas de laboratorio.

## 3. Reglas de comparabilidad (congeladas antes del primer prompt)

1. Un repositorio Git independiente por modelo, creado desde el **mismo commit seed** y sin compartir artefactos entre ramas. Un branch por módulo y checkpoint de código tras cada aceptación.
2. Mismo entorno Android SDK/JDK/Gradle, backend, MySQL, OS de prueba, datos semilla, escenario de red y versiones; congelar hashes. Misma versión de OpenCode y mismas herramientas disponibles. Aislar los logs del agente.
3. Dos modalidades posibles de contexto: **competencia de igualdad** (mismo contexto efectivo que ambos soportan y límites de salida) y **competencia de configuración real** (cada modelo en su perfil productivo, claramente etiquetada). Nunca mezclar las dos series.
4. Mismo prompt principal P00 y mismo prompt de módulo P01/P02/etc., versiones inmutables. El evaluador/autor de pruebas define casos antes de ver soluciones para impedir sesgo.
5. No realizar reparaciones manuales del código del candidato. Toda reparación debe proceder del propio modelo tras un prompt registrado. Excepción: fallos demostrados de infraestructura se documentan y se corrigen **simétricamente fuera de los candidatos**.
6. Cada corrección `FIX` usa **la misma plantilla estructural** con informe de fallos específico al resultado del modelo; no introducir pistas extra o soluciones literales a un único participante.
7. Cada test debe poder volver a ejecutarse. Los dos candidatos hacen una prueba de regresión de TODOS los módulos previamente aprobados.
8. Fin de intento cuando el modelo declara fin, termina el proceso, o alcanza el presupuesto definido. Definir límite de iteraciones y tiempo antes de la primera ejecución (propuesta: máximo 3 prompts de reparación por módulo y modelo, luego clasificar incompleto).
9. Capturar tiempos de generación, compilación, evaluación, latencia de inferencia; no confundirlos. En contextos largos registrar memoria GPU real, contexto servido y tokens procesados/generados.
10. Revisión humana de usabilidad con criterios precargados y misma persona/guion para ambas apps, sin conocer el modelo si es posible (A/B ciego). Registrar severidad, reproducción y evidencia por incidencia.

## 4. Secuencia modular y gates de aceptación

| ID | Entregable incremental | Gate mínimo para continuar |
|---|---|---|
| M00 | Arquitectura, estructura Android nativa + API/backend, Docker MySQL, SQLite, migraciones, CI, login de prueba, README | Arranca y compila, pruebas de conexión y configuración, ningún secreto embebido |
| M01 | Gestión de serenos y autenticación/roles + configuración de identificadores NFC | Crear/editar/desactivar sereno; roles; tag NFC único y revocable; validaciones |
| M02 | CRUD de puntos NFC y recorridos, asignación punto-recorrido, orden sugerido y tolerancias | Alta/baja lógica, unicidad, orden reproducible, cobertura de puntos |
| M03 | Inicio de ronda por tag NFC “Sereno”; elección de recorrido; lectura de puntos NFC con timestamp | Inicio no duplicado, asociación de actor y recorrido, registro inequívoco |
| M04 | Ejecución offline sobre SQLite y reinicio de app | Eventos sobreviven cierre/reinicio, estados correctos, sin pérdida de registros |
| M05 | Cierre de ronda con tag NFC “Sereno”, rondas incompletas, puntos omitidos, alerta de duración máxima | No autocierra por tiempo, no falsifica puntos, cierre auditado y restricciones |
| M06 | Sincronización Wi-Fi SQLite→API→MySQL, reintentos e idempotencia | Sin duplicados aun con reconexión/cortes/reenvío, integridad y trazabilidad |
| M07 | Panel backend de rondas, progreso, omisiones y alertas, exportación básica | Filtros por sereno/fecha/recorrido y evidencia verificable |
| M08 | Usabilidad industrial, NFC real, pruebas de batería, seguridad, accesibilidad y recuperación | Guion de campo repetible, criterios de latencia y consistencia aprobados |
| M09 (opcional) | Asistencia tercerizados por geocerca GPS: inicio/fin de jornada e incidencias | Separado del núcleo serenos y versionado individualmente |

Cada módulo agrega capacidad a un mismo producto por modelo; no reiniciar desde cero. No exigir características de módulos futuros en módulos anteriores. No permitir progreso automático con un módulo incompleto sin registrar deuda; decisión de continuar con deuda aplica igual a ambos.

## 5. Ciclo experimental por módulo

```text
CONGELAR PROMPT/PRUEBAS
       |
       v
[Pnn mismo prompt] ---Qwen----> commit candidato Qnn-0
                  \---Gemma----> commit candidato Gnn-0
       |                          |
       +---- build + test automatizado + evaluación de UX (mismo guion)
                              |
                       ¿gate PASS?
                    / YES         \ NO
               guardar checkpoint   FIX-nn-1 con reportes verificables
                                    |
                              nueva salida/commit
                                    |
                         re-test + regresión completa
                                    |
                        máximo FIX = 3 (propuesta)
       |
consolidar métricas y liberar prompt de siguiente módulo
```

El prompt maestro P00 se entrega solo al comienzo de cada rama y queda dentro del repositorio como referencia; el Pnn introduce sólo el módulo actual. El agente debe consultar el estado del código y decisiones previas, no inventar nuevas arquitecturas en cada prompt.

## 6. Sistema de puntuación: calidad a la primera y costo de correcciones

**Por módulo y modelo** registrar:
- `first_pass_rate`: casos de aceptación aprobados antes del primer FIX / casos ejecutados (reportar denominador).
- `gate_first_try`: booleano; 1 si TODAS las pruebas críticas y los requisitos obligatorios pasan en Pnn sin FIX, 0 en caso contrario.
- `fix_prompts`: número de mensajes adicionales posteriores a Pnn enviados para corregir defectos. NO cuentan aclaraciones idénticas para ambos antes de congelar Pnn, sí cuentan cambios de instrucción individualizados para un solo modelo.
- `turns_to_pass`: 1 + fix_prompts si se logra PASS; N/A si no pasa antes de límite.
- `final_pass_rate`: casos aprobados / casos ejecutados al último intento.
- `regression_failures`: cuántas pruebas de módulos anteriores dejan de pasar en cada iteración.
- `critical_failures`, `security_findings` (clasificados por severidad), `ux_blockers` (usabilidad guiada).
- `wall_generation_seconds`, `verification_seconds`, `total_elapsed_seconds`; `prompt_tokens`, `cached_prompt_tokens`, `generated_tokens`, `decode_tok_s`, `peak_vram_mb`, `effective_ctx_tokens`, `context_truncations`; marcar `N/D` si no se midió.
- `human_intervention`: clasificación (ninguna, diagnóstico, prompt FIX, infraestructura simétrica, parche manual prohibido).

**Indicadores principales recomendados, NO colapsar todo a un número:**
1. **First-pass module success:** módulos superados sin FIX / módulos intentados.
2. **Average FIX count per accepted module:** suma FIX / número de módulos aprobados. Menor es mejor; acompañar número de módulos fracasados.
3. **Critical acceptance rate:** pruebas críticas que pasan / pruebas críticas ejecutadas.
4. **Effort to accepted module:** tiempo total (generación + evaluación + corrección) para alcanzar PASS, o censura en límite.
5. **Regression count:** número de errores nuevos en funciones ya aprobadas.

Puntuación secundaria opcional (fijar antes de ejecutar): `efficiency_score = final_pass_rate * 100 / (1 + fix_prompts)` por módulo, **solo como indicador descriptivo**, siempre mostrar resultados primarios y marcar módulos que no alcanzaron gate. Una ejecución con 0 FIX pero 0 aprobaciones NO debe resultar ganadora de eficiencia.

Ejemplo ilustrativo (no experimental): Qwen M03 12/12 con 0 FIX, Gemma M03 12/12 con 2 FIX → ambos iguales en calidad final, pero Qwen mejor en first-pass y prompts requeridos; la comparación inversa puede ocurrir en otro módulo.

## 7. Prompts versión 1 (plantillas)

### P00 — prompt maestro idéntico para ambos modelos

```text
Actúa como ingeniero senior de Android nativo y backend Node.js/MySQL trabajando en ESTE repositorio existente.

Objetivo: desarrollar incrementalmente una aplicación para control de rondas de serenos. NO implementar todo el producto de una vez. En cada turno entrega SOLAMENTE el módulo solicitado y sus pruebas.

Normas:
- Inspecciona la arquitectura y archivos presentes antes de cambiarlos. No inventes APIs, columnas ni bibliotecas; explica toda incorporación necesaria.
- Conserva la funcionalidad aprobada y ejecuta las pruebas de regresión aplicables.
- Android nunca se conecta directamente a MySQL. Usar API autenticada; persistencia local SQLite/Room y sincronización futura cuando sea solicitada.
- No embebas contraseñas ni secretos. Diseña operaciones auditables e idempotentes cuando corresponda.
- No realices cambios ajenos al módulo. Prioriza cambios localizados.
- Si faltan herramientas o infraestructura, informa qué verificación no fue posible. No declares PASS sin ejecutarla.
- Entrega: resumen de archivos modificados; decisiones técnicas; comandos de build/test; resultados con evidencia; limitaciones y pendientes.
- No solicites intervención humana para reparar el código. Si hay un error de compilación/ejecución provocado por tus cambios, intenta corregirlo dentro del turno.
- El prompt de módulo y sus criterios de aceptación controlan el alcance de cada iteración.
```

### Pnn — prompt de módulo común

```text
MÓDULO: <Mn — nombre>.
Punto de partida: commit <seed/checkpoint idéntico por protocolo>.
Alcance incluido: <requisitos medibles>.
Fuera de alcance: <módulos siguientes>.
Casos de aceptación: <IDs y condiciones dadas antes de ejecutar>.
Interfaz/UX: <pasos observables en dispositivo>.
Restricciones: conservar módulos previos; sin modificaciones especulativas.

Implementa el módulo. Ejecuta build, pruebas del módulo y regresión disponible. Entrega evidencia de resultados, archivos cambiados y limitaciones. No avances al próximo módulo.
```

### FIX-nn-k — prompt correctivo con plantilla IGUAL, pero evidencia propia

```text
Corrección controlada FIX-<nn>-<k> de SERENOS-CODE-001.
No cambies alcance ni arquitectura salvo que sea imprescindible y justificable.
Resultado observado por evaluador independiente:
- Pruebas fallidas: <IDs>.
- Pasos mínimos para reproducir: <pasos>.
- Esperado: <salida observable>.
- Actual: <salida/log sanitizado>.
- Regresiones: <IDs>.
- Restricciones: no modificar tests ni desactivar validaciones.

Inspecciona únicamente el código relevante, identifica causa, aplica reparación mínima y ejecuta pruebas/regresión. Entrega resumen y evidencia verificable. No avances al siguiente módulo.
```

### M00 — primer módulo listo para desarrollar

```text
M00: Infraestructura mínima de aplicación de serenos, SIN implementar rondas todavía.
Construye:
1) Proyecto Android nativo Kotlin compilable y pantalla principal con estado de conexión.
2) Backend Node.js con /health y configuración por variables de entorno; MySQL en Docker Compose, migraciones mínimas versionadas y una prueba de conexión.
3) Persistencia SQLite/Room local con prueba automatizada básica de crear y recuperar un evento de ejemplo, SIN sincronizar aún.
4) README reproducible, scripts de arranque, tests backend y pipeline local mínimo.
5) Registro local de configuración del backend por URL (no conexión directa a MySQL ni contraseñas integradas en APK).

Gate: compilación Android; backend healthy; tests de base; SQLite conserva evento tras reiniciar componente; ningún secreto hardcoded; APK ejecuta en Android de pruebas. No construir funcionalidades NFC, serenos, rondas ni terceros todavía.
```

## 8. Estructura de evidencias sugerida

```text
benchmarks/SERENOS-CODE-001/
  PROTOCOL.md
  prompts/P00.md
  prompts/M00.md
  prompts/M01.md
  prompts/FIX-TEMPLATE.md
  test-specs/M00-acceptance.md
  runs/
    QWEN/M00/attempt-0/{manifest.json,build.log,tests.json,metrics.json}
    QWEN/M00/fix-1/{...}
    GEMMA/M00/attempt-0/{...}
  results/SCORECARD.md
```

Use JSON manifests with `model`, `quantization`, `reasoning`, `model_sha256`, `server_commit`, `ctx_requested`, `ctx_effective`, `gpu`, `opencode_version`, `prompt_sha256`, `seed_commit`, `run_id`, `timestamps_utc`, `exit_code`, `tests_total`, `tests_passed`, `critical_failures`, `fix_count`, `generation_wall_s`, `total_wall_s`, `generated_tokens`, `peak_vram_mb`, `evidence_paths`. Never commit secrets, private .env, JWT, personal location history, or employee IDs.

## 9. Before the first run

Confirm Android SDK versions and tested device NFC API; freeze M00 acceptance tests and tools; confirm equal context or label 'native configuration'; snapshot seed; preflight health; establish log collectors for llama.cpp metrics and GPU memory; use neutral experiment identifiers rather than model brand in user-visible UX. Then start P00+M00 independently for each model and **do not reveal evaluator source**.
