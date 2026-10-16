# GEMMA4-LAB-001 — Cierre de campaña BENCH-CODE-001

**Fecha:** 2026-10-16. **Estado:** cerrada la generación y evaluación de cuatro perfiles. Se conservan sin modificar los candidatos originales.

## Resultados

| Configuración | Generación | Salida OpenCode | Evaluación funcional |
|---|---:|---:|---|
| Q3_K_M Thinking OFF, intento 1 | 337 s | 0 | No evaluado |
| Q3_K_M Thinking OFF, intento 2 | 205 s | 0 | Bloqueada en `db:init`; pruebas no iniciadas |
| Q3_K_M Thinking ON | 377 s | 1 | 16/16, 14/14 críticas, PASS |
| IQ4_XS Thinking OFF | 758 s | 0 | Fallo al instalar dependencia; pruebas no iniciadas |
| IQ4_XS Thinking ON | 392 s | 0 | 13/16, 11/14 críticas, FAIL |

Referencia Qwen3-Coder Q3: tres ensayos independientes con 16/16 y 14/14 críticas, 436, 567, 586 s; promedio 529,7 s. Gemma Q3 ON tardó 28,8% menos que ese promedio en una sola ejecución, sin inferencia estadística. El sistema Windows cambió entre campañas: `10.0.26200` a `10.0.26300`.

## Hallazgos confirmados

- **Gemma Q3 OFF:** la inicialización de esquema terminó, pero `src/db/init.js` dejó abierto el pool MySQL y `npm run db:init` no finalizó. Sin puntuación de tests.
- **Gemma IQ4 OFF:** `package.json` no tenía sección de dependencias; el `package-lock.json` sí enumeraba ocho, incluida `mysql2`. `npm install` auditó un solo paquete; `db:init` terminó en `Cannot find module 'mysql2/promise'`. Sin puntuación de tests.
- **Gemma IQ4 ON, T10:** usuario propietario podía consultar registros pero `PUT` dio HTTP 500.
- **Gemma IQ4 ON, T12:** otro usuario obtuvo HTTP 500 intentando PUT sobre un registro ajeno; DELETE 404, GET del propietario 200. No hay evidencia de modificación indebida.
- **Causa común confirmada de T10/T12:** `src/services/recordService.js` genera SQL mal formado: elimina la coma al final de las asignaciones y agrega `updated_at` sin coma de separación.
- **Gemma IQ4 ON, T15:** tras reinicio, health, login y listado HTTP 200; no encontró el título persistente esperado. El evaluador establece `persistent_title` al título que debería resultar de la actualización (`ALICE_UPDATED_TITLE`). La actualización fallida explica sólidamente la ausencia del título esperado; **T15 no prueba pérdida física de datos**. `db/schema.sql` contiene `CREATE TABLE IF NOT EXISTS`, sin borrado de tablas.
- **IQ4 ON seguridad de dependencias:** `npm install` informó tres vulnerabilidades high, sin desglose disponible.
- **Gemma Q3 ON:** la evaluación funcional fue completamente satisfactoria pese a la salida OpenCode `1`. Registrar ambos campos por separado.

## Identificadores y rutas

- Congelado histórico `LocalAI-Lab-freeze`: commit `23bed848a1467225a0858dbdb27e57ef2e9aa474`.
- SHA256 prompt: `e1ec6e63a2a603a4d5591158a262d66de1f838a93e72d03ae2a158827e35dbac`.
- SHA256 seed: `a1d24686ddf69b8d5eb69b956b1500fafa92aac8658270deff33ba3e2c1eadc7`.
- Evaluador externo privado v1.0.0: SHA256 `0098e69f2f1d8e18e56b4de1b8132f3baa08eaaf2151c0f06ddf8bf296693903` (no incorporar código ni estado con tokens a Git).
- OpenCode `1.18.27`, 32768 tokens, Node `24.19.0`, npm `11.17.0`, Docker `29.8.0`, Compose `v5.5.1`.
- Run root `C:\bench-code-001-formal\GEMMA4-C001-RUNS`.
- Config SHA256 Q3 ON: `d961e23b8aa5464b58ed8f1eb954ae4947c412fcee26b65327f952f084d5972b`.
- Config SHA256 IQ4 OFF: `0ed089c724246f2f78839dc856d986e945760f5f06af87efc1eabbededd12274`.
- Config SHA256 IQ4 ON: `0052df6c80ada447cc5e379c0b2e4bbe49939b2e4c8742d655a27179eafc0b70`.

## Conclusión

Para el siguiente ensayo de generación de código de la aplicación de rondas de serenos, usar **Gemma 4 Q3_K_M Thinking ON** frente al **Qwen3-Coder** vigente. Serán experimentos nuevos: mismo alcance, requisitos, base de código, política de intervención, casos de prueba y mecanismos de medición; registrar el contexto real servido y la diferencia de recursos por modelo.

Ver también `GEMMA4-LAB-001-2026-10-16.md` y `GEMMA4-LAB-001-OPERATIONS-INDEX.md`.
