# BENCH-CODE-DEV-002 — Gestión de vehículos de transportistas

Trabaja sobre el repositorio entregado. Implementa completamente la funcionalidad solicitada y deja el proyecto en estado ejecutable.

## Objetivo
Agregar al panel administrativo la gestión de vehículos asociados a transportistas.

## Datos de vehículo
Cada vehículo debe tener:
- id
- transportista_id
- matricula
- marca
- modelo
- activo
- created_at / updated_at (o los timestamps equivalentes usados por el proyecto)

## Requisitos funcionales
1. Persistencia MySQL integrada con la arquitectura existente.
2. `transportista_id` es obligatorio y debe referenciar un transportista existente.
3. `matricula` es obligatoria y única.
4. CRUD administrativo completo y protegido por la autenticación admin existente.
5. Deben existir, como mínimo, estas operaciones HTTP bajo `/api/admin/vehicles`:
   - POST `/api/admin/vehicles`
   - GET `/api/admin/vehicles`
   - GET `/api/admin/vehicles/:id`
   - PUT `/api/admin/vehicles/:id`
   - DELETE `/api/admin/vehicles/:id`
6. GET de listado debe permitir identificar el transportista asociado (por empresa y/o nombre).
7. Crear o actualizar con transportista inexistente debe ser rechazado con HTTP 4xx.
8. Matrícula duplicada debe ser rechazada con HTTP 4xx.
9. GET/PUT/DELETE de un vehículo inexistente debe devolver HTTP 404.
10. El panel administrativo debe permitir listar, crear, editar y eliminar vehículos.
11. Al editar, el formulario debe cargar los datos actuales y guardar mediante PUT.
12. Cancelar una edición debe volver al listado sin modificar datos.
13. Para facilitar pruebas E2E, agrega estos atributos estables al frontend:
    - contenedor/sección: `data-testid="vehicles-section"`
    - botón nuevo: `data-testid="vehicle-new"`
    - formulario: `data-testid="vehicle-form"`
    - campo transportista: `data-testid="vehicle-transporter"`
    - campo matrícula: `data-testid="vehicle-matricula"`
    - campo marca: `data-testid="vehicle-marca"`
    - campo modelo: `data-testid="vehicle-modelo"`
    - guardar: `data-testid="vehicle-save"`
    - cancelar: `data-testid="vehicle-cancel"`
    - cada fila: `data-testid="vehicle-row"`
    - botón editar de cada fila: `data-testid="vehicle-edit"`
    - botón eliminar de cada fila: `data-testid="vehicle-delete"`
14. Los datos deben persistir después de reiniciar la aplicación.
15. No rompas las funciones existentes de usuarios, transportistas, autenticación ni otras rutas.
16. Mantén el estilo y arquitectura del repositorio; evita reescrituras innecesarias.

## Restricciones del benchmark
- Puedes inspeccionar, modificar y ejecutar el proyecto.
- No hay intervención humana durante la corrida.
- No se proporcionan los tests del evaluador.
- No cambies puertos, credenciales o infraestructura externa salvo que sea imprescindible para el código del proyecto.
- Termina cuando consideres que la implementación está completa.
