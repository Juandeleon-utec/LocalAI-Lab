# M00 — Infraestructura de la APP Serenos

Implementa el primer módulo exclusivamente, en el repositorio proporcionado, de acuerdo con P00-MASTER.md.

Alcance:
1. Proyecto Android NATIVO Kotlin compilable con pantalla principal sencilla y estado de conexión a backend.
2. Backend Node.js con GET /health y configuración mediante variables de entorno. MySQL en Docker Compose y migraciones mínimas versionadas, más prueba reproducible de conexión.
3. SQLite/Room local para registrar y recuperar un evento de ejemplo; prueba automatizada que demuestre persistencia entre aperturas.
4. Configuración editable de URL del backend en Android; NO acceder directamente a MySQL ni introducir secretos en APK.
5. Scripts de arranque, README de instalación y tests mínimos automatizados.

Fuera de alcance M00: NFC, fichado de serenos, puntos, rondas, gestión de recorridos, sincronización offline-online, reportes, asistencia de tercerizados.

Aceptación:
- Android compila sin intervención externa de edición de código.
- Backend compila/inicia, health responde y conexión MySQL se valida.
- La migración/instalación inicial es reproducible.
- La persistencia local de un evento es verificable.
- No existen credenciales hardcodeadas ni acceso directo Android→MySQL.
- Se puede ejecutar una pantalla inicial en un emulador o dispositivo de prueba.

Entrega las pruebas realizadas y sus logs, lista de archivos y limitaciones. No implementes M01.
