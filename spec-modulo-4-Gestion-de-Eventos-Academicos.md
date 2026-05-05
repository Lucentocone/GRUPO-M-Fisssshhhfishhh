# Spec – Módulo: Gestión de Eventos Académicos

---

## 1. Objetivo y Contexto

### Objetivo
Permitir a los organizadores crear, configurar, publicar y administrar eventos académicos (cursos, jornadas, congresos, charlas, entre otros), controlando su ciclo de vida completo desde el borrador hasta el cierre, y exponiendo el listado público de eventos para que los participantes puedan consultarlos e inscribirse.

### Contexto
Este módulo es el núcleo central del sistema. Todos los demás módulos (Inscripción, Acreditación, Certificados, Reportes) dependen de que exista un evento correctamente configurado. Un organizador debe poder definir todos los atributos del evento antes de publicarlo, y el sistema debe garantizar que solo eventos válidos y completos sean visibles al público.

El listado de eventos es de acceso público (sin autenticación), mientras que la creación y administración requiere el rol `organizador`. Los participantes interactúan con este módulo únicamente en modo lectura (consulta y filtrado).

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU 4.1 – Crear un evento académico
**Como** organizador,
**quiero** crear un nuevo evento académico con todos sus datos,
**para** configurarlo y publicarlo cuando esté listo.

**Criterios de Aceptación:**
- El formulario de creación debe solicitar: título, descripción, tipo de evento (curso / jornada / congreso / charla / otro), fecha y hora de inicio, fecha y hora de fin, modalidad (presencial / virtual / híbrida), lugar o enlace, cupo mínimo (opcional), cupo máximo (opcional) y fecha límite de inscripción (opcional).
- Todos los campos obligatorios deben validarse antes de guardar.
- Al crear, el evento queda en estado `borrador` y no es visible en el listado público.
- El sistema asigna automáticamente al usuario creador como organizador del evento.
- La fecha de fin no puede ser anterior a la fecha de inicio.
- La fecha límite de inscripción no puede ser posterior a la fecha de inicio del evento.

### HU 4.2 – Editar un evento
**Como** organizador,
**quiero** modificar los datos de un evento que aún no fue publicado o que está publicado,
**para** corregir o actualizar la información antes o durante su vigencia.

**Criterios de Aceptación:**
- Se pueden editar todos los campos mientras el evento esté en estado `borrador` o `publicado`.
- No se puede editar un evento en estado `finalizado` o `cancelado`.
- Si se reduce el cupo máximo a un valor menor que los inscriptos actuales, el sistema debe bloquear la acción y mostrar un mensaje descriptivo.
- Los cambios se persisten inmediatamente y se reflejan en el listado público si el evento ya estaba publicado.

### HU 4.3 – Publicar un evento
**Como** organizador,
**quiero** publicar un evento cuando esté listo,
**para** que aparezca en el listado público y los participantes puedan inscribirse.

**Criterios de Aceptación:**
- Solo se puede publicar un evento que esté en estado `borrador`.
- Para poder publicar, el evento debe tener título, descripción, tipo, fecha de inicio y fin, y modalidad completos.
- Al publicar, el estado cambia a `publicado` y el evento aparece en el listado público.
- El sistema registra la fecha y hora de publicación.

### HU 4.4 – Cancelar un evento
**Como** organizador,
**quiero** cancelar un evento publicado,
**para** informar a los inscriptos que el evento no se realizará.

**Criterios de Aceptación:**
- Solo se puede cancelar un evento en estado `publicado`.
- Al cancelar, el estado cambia a `cancelado` y el evento deja de aceptar nuevas inscripciones.
- El sistema debe notificar por email a todos los participantes inscriptos sobre la cancelación.
- El evento cancelado sigue visible en el listado con su estado indicado claramente, pero no permite inscripciones.

### HU 4.5 – Consultar listado público de eventos
**Como** visitante o participante,
**quiero** ver el listado de eventos disponibles con filtros,
**para** encontrar los eventos de mi interés e inscribirme.

**Criterios de Aceptación:**
- El listado es accesible sin autenticación.
- Solo se muestran eventos en estado `publicado` y `finalizado` (los cancelados se muestran con etiqueta visual diferenciada).
- Los eventos se ordenan por fecha de inicio ascendente por defecto.
- Filtros disponibles: por tipo de evento, por modalidad, por estado (próximos / pasados / todos), y por rango de fechas.
- Cada tarjeta del listado muestra: título, tipo, fecha, modalidad, lugar/enlace, cupos disponibles (si aplica) y estado de inscripción (abierta / cerrada / agotado).
- Si no hay eventos que coincidan con los filtros, se muestra un mensaje descriptivo de "empty state".

### HU 4.6 – Ver detalle de un evento
**Como** visitante o participante,
**quiero** ver la información completa de un evento,
**para** decidir si inscribirme.

**Criterios de Aceptación:**
- La página de detalle es accesible sin autenticación.
- Muestra todos los datos del evento: título, descripción completa, tipo, fechas, modalidad, lugar/enlace, cupos (disponibles y totales si el organizador lo permite), fecha límite de inscripción y listado de disertantes (si están cargados).
- Muestra un botón de inscripción activo si las condiciones lo permiten (evento publicado, cupo disponible, fecha límite no vencida), o el motivo por el que no se puede inscribir en caso contrario.

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Requisitos Funcionales
- **RF-4.1:** El sistema debe permitir crear eventos con todos sus atributos configurables.
- **RF-4.2:** El sistema debe gestionar el ciclo de vida del evento mediante estados: `borrador` → `publicado` → `finalizado` / `cancelado`.
- **RF-4.3:** El sistema debe exponer un endpoint público de listado con soporte de filtros y paginación.
- **RF-4.4:** El sistema debe exponer un endpoint público de detalle de evento.
- **RF-4.5:** El sistema debe calcular y exponer los cupos disponibles en tiempo real (cupo_maximo - inscriptos_confirmados).
- **RF-4.6:** El sistema debe marcar automáticamente un evento como `finalizado` cuando su fecha de fin haya pasado y esté en estado `publicado`.
- **RF-4.7:** El sistema debe notificar por email a los inscriptos si el evento es cancelado.

### Reglas de Negocio
- **RN-4.1:** Un evento solo puede ser creado por un usuario con rol `organizador`.
- **RN-4.2:** El estado `borrador` solo es visible para el organizador del evento, nunca en el listado público.
- **RN-4.3:** Si se define `cupo_maximo`, el sistema no puede aceptar más inscripciones que ese valor.
- **RN-4.4:** Si se define `cupo_minimo` y al llegar la fecha de inicio no se alcanzó, el sistema debe alertar al organizador (no cancela automáticamente; la decisión es del organizador).
- **RN-4.5:** La fecha límite de inscripción, si no se define, es igual a la fecha de inicio del evento.
- **RN-4.6:** Un evento `finalizado` o `cancelado` no puede volver a estados anteriores.
- **RN-4.7:** Todo evento debe tener al menos un organizador en todo momento.

---

## 4. Restricciones Técnicas Específicas de este Módulo

- **RT-4.1:** El listado público de eventos debe estar paginado en el backend (máximo 20 eventos por página) para evitar respuestas masivas.
- **RT-4.2:** El cálculo de cupos disponibles debe hacerse en el backend (nunca en el cliente) para evitar condiciones de carrera con el módulo de Inscripción.
- **RT-4.3:** La transición automática a estado `finalizado` debe implementarse mediante un job programado (cron) que se ejecute al menos una vez por hora.
- **RT-4.4:** Los endpoints de solo lectura (listado y detalle) no requieren autenticación. Los endpoints de escritura (crear, editar, publicar, cancelar) requieren JWT con claim de rol `organizador`. Ver `Contracts.md` para el formato de respuestas y autenticación.
- **RT-4.5:** Los filtros del listado deben procesarse en el backend mediante parámetros de query (`?tipo=congreso&estado=proximo&page=1`), nunca filtrando en memoria en el servidor sobre colecciones completas.
- **RT-4.6:** El campo `tipo` debe ser un ENUM cerrado en base de datos para garantizar integridad. La incorporación de nuevos tipos requiere una migración controlada.

---

## 5. Modelo de Datos de este Módulo

### Entidad: `Evento`
| Campo | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id_evento` | UUID | PK | Identificador único |
| `id_organizador` | UUID | FK → Usuario, NOT NULL | Usuario creador del evento |
| `titulo` | VARCHAR(200) | NOT NULL | Nombre del evento |
| `descripcion` | TEXT | NOT NULL | Descripción completa |
| `tipo` | ENUM | NOT NULL | `curso`, `jornada`, `congreso`, `charla`, `otro` |
| `modalidad` | ENUM | NOT NULL | `presencial`, `virtual`, `hibrida` |
| `estado` | ENUM | NOT NULL, DEFAULT `borrador` | `borrador`, `publicado`, `finalizado`, `cancelado` |
| `fecha_inicio` | DATETIME | NOT NULL | Inicio del evento |
| `fecha_fin` | DATETIME | NOT NULL | Fin del evento (debe ser > fecha_inicio) |
| `lugar_o_enlace` | VARCHAR(500) | NULLABLE | Dirección física o URL |
| `cupo_minimo` | INTEGER | NULLABLE, CHECK > 0 | Cupo mínimo para realizarse |
| `cupo_maximo` | INTEGER | NULLABLE, CHECK > 0 | Límite de inscriptos |
| `fecha_limite_inscripcion` | DATETIME | NULLABLE | Cierre de inscripciones (DEFAULT = fecha_inicio) |
| `fecha_publicacion` | DATETIME | NULLABLE | Timestamp de la publicación |
| `creado_el` | DATETIME | NOT NULL, DEFAULT NOW() | Fecha de creación del registro |
| `actualizado_el` | DATETIME | NOT NULL | Última modificación |

### Entidad: `Actividad` (cronograma del evento)
| Campo | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id_actividad` | UUID | PK | Identificador único |
| `id_evento` | UUID | FK → Evento, NOT NULL | Evento al que pertenece |
| `titulo` | VARCHAR(200) | NOT NULL | Nombre de la actividad |
| `descripcion` | TEXT | NULLABLE | Detalle de la actividad |
| `hora_inicio` | DATETIME | NOT NULL | Inicio de la actividad |
| `hora_fin` | DATETIME | NOT NULL | Fin de la actividad |
| `sala_o_enlace` | VARCHAR(200) | NULLABLE | Sala o URL específica |
| `id_disertante` | UUID | FK → Usuario, NULLABLE | Disertante asignado |

---

## 6. Plan de Tareas

| Ticket | Descripción | Depende de | Estimación |
|---|---|---|---|
| **T-4.1** | BD: Crear tabla `Evento` con sus restricciones, índices y ENUMs | — | 2h |
| **T-4.2** | BD: Crear tabla `Actividad` con FK a Evento | T-4.1 | 1h |
| **T-4.3** | API: `POST /eventos` – Crear evento (requiere JWT organizador) | T-4.1 | 3h |
| **T-4.4** | API: `PUT /eventos/{id}` – Editar evento con validaciones de estado | T-4.3 | 3h |
| **T-4.5** | API: `PATCH /eventos/{id}/publicar` – Transición borrador → publicado | T-4.4 | 2h |
| **T-4.6** | API: `PATCH /eventos/{id}/cancelar` – Transición publicado → cancelado + notificación email | T-4.5 | 3h |
| **T-4.7** | API: `GET /eventos` – Listado público con filtros y paginación | T-4.1 | 4h |
| **T-4.8** | API: `GET /eventos/{id}` – Detalle público con cupos en tiempo real | T-4.7 | 2h |
| **T-4.9** | API: CRUD de `Actividad` (`POST /eventos/{id}/actividades`, etc.) | T-4.2 | 3h |
| **T-4.10** | Cron job: Transición automática publicado → finalizado al vencer fecha_fin | T-4.5 | 2h |
| **T-4.11** | QA: Tests unitarios, de integración y smoke test | T-4.8, T-4.10 | 3h |

**Estimación total: ~28 horas**

---

## 7. Estrategia de Verificación

### Pruebas Unitarias
- **PU-4.1:** Verificar que el servicio rechace la creación de un evento con `fecha_fin < fecha_inicio` → Error HTTP 422.
- **PU-4.2:** Verificar que no se pueda publicar un evento con campos obligatorios incompletos → HTTP 422.
- **PU-4.3:** Verificar que no se pueda editar un evento en estado `finalizado` → HTTP 409.
- **PU-4.4:** Verificar que la reducción de `cupo_maximo` a un valor menor que los inscriptos actuales sea bloqueada → HTTP 409.
- **PU-4.5:** Verificar que la transición de estado solo siga los caminos permitidos (ej: `cancelado` → `publicado` debe fallar).

### Pruebas de Integración
- **PI-4.1:** Crear evento → publicar → verificar que aparece en `GET /eventos` → inscribir un participante → verificar que el cupo disponible se reduce en 1.
- **PI-4.2:** Crear evento → publicar → cancelar → verificar que los inscriptos reciben email de cancelación → verificar que no se aceptan nuevas inscripciones.
- **PI-4.3:** Crear evento con `fecha_fin` en el pasado → publicar → ejecutar cron → verificar que el estado cambia a `finalizado`.

### Prueba de Humo (Smoke Test)
- **PS-4.1:** Flujo completo sin autenticación: ingresar a `GET /eventos` → aplicar filtro por tipo → ver detalle de un evento → verificar que el botón de inscripción está activo.
- **PS-4.2:** Flujo de organizador: login → crear evento → completar datos → publicar → verificar aparición en listado público.

### Criterio de Aceptación General
El módulo se considera completo cuando: (1) un organizador puede llevar un evento desde `borrador` hasta `finalizado` o `cancelado` sin errores, (2) el listado público refleja correctamente los estados y cupos en tiempo real, y (3) todos los criterios de aceptación de las HU 4.1 a 4.6 están verificados.
