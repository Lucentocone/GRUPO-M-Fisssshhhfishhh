# Spec – Módulo: Generación de Reportes

---

## 1. Alcance y Contexto

### Objetivo
Brindar al organizador de herramientas para consultar, visualizar y exportar las métricas operativas del evento (inscripciones, presentismo, agenda). Estos reportes facilitan la toma de decisiones y sirven como respaldo documental oficial.

### Contexto de Arquitectura y Negocio
A medida que el evento avanza, se necesita consolidar la información que vive dispersa en distintos dominios (Inscripción, Acreditación, Encuestas) en artefactos legibles y exportables. 

Este módulo funciona estrictamente como una capa de agregación y lectura (Read-Only). No muta el estado del negocio, sino que formatea los datos de otros módulos. Aunque los reportes pueden emitirse en cualquier momento, los de "Asistencia" alcanzan su valor real post-evento.

---

## 2. Historias de Usuario y Criterios de Aceptación 

### HU 5.1: Reporte de inscriptos
Como organizador, quiero exportar la lista de inscriptos, para medir la demanda real y planificar la logística.

Criterios de Aceptación:
*   **Información expuesta:** Nombre completo, DNI, email, rol, fecha de inscripción y modalidad.
*   **Filtros:** Por rol, modalidad y rango de fechas.
*   **Métricas UI:** Header indicando la ocupación actual (ej. "87 / 120 cupos cubiertos").
*   **Formatos:** Exportable a PDF y CSV.
*   **SLA de Performance:** Generación en `< 10 segundos` para payloads de hasta 500 registros.

> **🔐 [OWASP] Criterios de Aceptación de Seguridad — Enriquecimiento (A01:2021 · Broken Access Control)**
>
> El endpoint de exportación expone datos personales sensibles (DNI, email) de todos los inscriptos. El riesgo de control de acceso roto aplica directamente: un usuario sin rol `organizador` podría solicitar el reporte directamente vía URL manipulada, obteniendo el padrón completo del evento.
>
> *   **[OWASP-A01] Validación de autorización server-side:** El backend debe verificar en cada request que el `id_usuario` presente en el JWT tiene el rol `organizador` **y** es propietario del evento (`id_evento`) solicitado. Esta validación debe ocurrir en la capa de controladores, independientemente de que el botón de exportación esté oculto en la UI para usuarios sin permisos.
>     *   Test: Solicitar `GET /eventos/{id}/reportes/inscripciones` con un JWT de rol `participante` → debe retornar **HTTP 403 Forbidden**.
>     *   Test: Solicitar el reporte de un evento ajeno con un JWT de `organizador` de otro evento → debe retornar **HTTP 403 Forbidden**.
> *   **[OWASP-A03] Sanitización de parámetros de filtro:** Los filtros de consulta (`fecha_desde`, `fecha_hasta`, `rol`, `modalidad`) deben ser validados y tipados antes de ser utilizados en queries a la base de datos. Deben usarse consultas parametrizadas (prepared statements) para prevenir inyección SQL.
>     *   Test: Enviar `fecha_desde=1' OR '1'='1` → debe retornar HTTP 400 Bad Request sin ejecutar ninguna consulta.
> *   **[OWASP-A02] Canal seguro obligatorio:** Los endpoints de exportación deben estar disponibles únicamente sobre HTTPS. Cualquier solicitud HTTP no cifrada debe redirigirse con **301** o rechazarse. El archivo descargado no debe contener más datos de los estrictamente necesarios (principio de minimización).

### HU 5.2: Reporte de presentismo (Post-evento)
Como organizador, quiero un informe de asistencia real, para auditar a quiénes corresponde el certificado y analizar el *drop-off* de inscriptos vs. asistentes.

Criterios de Aceptación:
*   **Inforamción expuesta:** Nombre completo, DNI, estado (presente/ausente), timestamp de ingreso y método (QR/Manual).
*   **Métricas UI:** Resumen con total inscriptos, total acreditados y % de asistencia.
*   **Permisos:** Exclusivo para el rol `organizador` del evento en cuestión.
*   **Edge case:** Si se intenta generar antes de la fecha del evento, mostrar un *warning* indicando que la data de asistencia aún no es definitiva.
*   **Formatos:** PDF y CSV.

> **🔐 [OWASP] Criterios de Aceptación de Seguridad — Enriquecimiento (A09:2021 · Security Logging and Monitoring Failures)**
>
> El reporte de presentismo es el artefacto más sensible del módulo: combina datos personales con información de comportamiento (timestamp de ingreso, método de acceso). El acceso indebido o no auditado a este reporte representa una violación de privacidad grave. OWASP A09 exige que los eventos de acceso a datos sensibles sean registrados de forma confiable.
>
> *   **[OWASP-A09] Registro de auditoría completo:** Cada generación o descarga del reporte de presentismo debe registrarse en la tabla `Audit_Reportes` con: `id_usuario`, `id_evento`, `tipo = 'asistencia'`, `formato`, `ip_origen` y `timestamp`. Este log no debe poder ser eliminado ni modificado por ningún rol de la aplicación.
>     *   Test: Descargar el reporte de asistencia → verificar que se insertó un registro en `Audit_Reportes` con los campos correctos.
>     *   Test: Intentar eliminar un registro de `Audit_Reportes` desde la API → debe retornar **HTTP 405 Method Not Allowed** (endpoint de solo escritura/lectura, sin DELETE).
> *   **[OWASP-A01] Re-validación de ownership en asistencia:** Dado que los timestamps de ingreso pueden usarse para perfilar comportamientos, el control de acceso debe ser especialmente estricto. Si el token JWT no contiene el claim `organizador` del evento específico, el servidor debe retornar **HTTP 403** sin revelar si el evento existe o no (respuesta genérica para evitar enumeración).
> *   **[OWASP-A04] Rate limiting en exportación:** Para prevenir la extracción masiva y automatizada de datos de asistentes, el endpoint debe implementar un límite de solicitudes por usuario (ej. máximo 10 exportaciones por hora por `id_usuario`). Al superarse, retornar **HTTP 429 Too Many Requests**.

### HU 5.3: Generación de agenda
Como organizador, quiero compilar el cronograma en un documento formal, para distribuirlo a los asistentes y disertantes.

Criterios de Aceptación:
*   Se nutre directamente del módulo de Gestión de Eventos.
*   **Info expuesta:** Título del evento, fecha, lugar y timeline ordenado (Actividad, horario, disertante, sala).
*   **Branding:** El PDF inyecta el logo y nombre del evento en el header.
*   **Flujo:** Permite preview en pantalla antes de gatillar la descarga.
*   **Edge case:** Si el evento no tiene cronograma cargado, bloquea la acción y ofrece un deep-link para ir a configurarlo.

### HU 5.4: Dashboard de métricas (Overview)
Como organizador, quiero un panel centralizado con los KPIs del evento, para monitorear la salud del evento de un vistazo.

Criterios de Aceptación:
*   **KPIs mostrados:** Inscriptos totales, cupo restante, acreditados, certificados emitidos y rating promedio de encuestas.
*   Actualización *on-mount* (al cargar la vista).
*   **Navegabilidad:** Cada tarjeta de KPI funciona como un acceso directo al reporte detallado.

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Requisitos Funcionales (RF)
*   **RF-5.1 | Reportes:** Capacidad de generar reportes paramétricos de inscripciones y asistencia.
*   **RF-5.2 | Agenda:** Generación automática de PDF basada en el cronograma.
*   **RF-5.3 | Dashboard:** Vista de resumen con agregación de KPIs.
*   **RF-5.4 | Exportación:** Soporte nativo para descargas en PDF y CSV.
*   **RF-5.5 | Audit Log:** Registro en base de datos de quién generó qué reporte y cuándo.

### Reglas de Negocio (RN)
*   **RN-5.1 | Multitenancy:** Aislamiento estricto. Un organizador solo puede consultar la data de los eventos que administra.
*   **RN-5.2 | Dependencia de data:** El reporte de asistencia exige al menos 1 registro en el módulo de Acreditación. Si está vacío, se arroja un *empty state* descriptivo.
*   **RN-5.3 | Dependencia de agenda:** No se puede emitir el PDF de agenda sin al menos 1 actividad cargada.
*   **RN-5.4 | Snapshots:** Los archivos exportados representan una "foto" del momento. No hay actualización dinámica del archivo ya descargado.

---

## 4. Restricciones Técnicas (Tech Specs)

*   **RT-5.1 | Motor PDF:** El renderizado ocurre 100% del lado del servidor para garantizar fidelidad en cualquier cliente. *(Sugerencia: iText en Java o WeasyPrint/ReportLab en Python)*.
*   **RT-5.2 | Encoding:** Los CSV deben generarse en `UTF-8 con BOM` para evitar que Excel rompa los caracteres especiales en Windows.
*   **RT-5.3 | Read-Only:** Prohibido inyectar lógica de escritura en entidades de otros módulos. Solo `SELECTs` (o vistas materializadas si la performance lo amerita).
*   **RT-5.4 | Paginación:** Endpoints de reportes masivos deben estar paginados en el backend (máximo 200 rows/página) o usar *streaming* de datos para evitar timeouts.
*   **RT-5.5 | i18n & Fuentes:** El template PDF debe embeber tipografías que soporten caracteres latinos (tildes, ñ) para evitar fallos de renderizado.
*   **RT-5.6 | Auth:** Endpoints protegidos mediante JWT validando el claim de rol `organizador` y el ownership del evento.

---

## 5. Modelo de Datos (Capa de Lectura)

Este módulo consume datos de otros dominios. El mapeo de dependencias es:

| Entidad Origen | Módulo Dueño | Campos Consumidos |
|---|---|---|
| `Evento` | Mód. 1 (Eventos) | ID, título, fecha, cupo, estado |
| `Actividad` | Mód. 1 (Eventos) | ID, evento_id, título, horarios, disertante, sala |
| `Inscripcion` | Mód. 2 (Inscripciones) | ID, evento_id, usuario_id, fecha, modalidad, estado |
| `Acreditacion` | Mód. 3 (Acreditaciones) | inscripción_id, timestamp, método, anulada |
| `Certificado` | Mód. 4 (Certificados) | inscripción_id, tipo, fecha |
| `Usuario` | IAM / Auth | ID, nombre, apellido, DNI, email |

### Tabla Propia: `Audit_Reportes` (Logs)
| Campo | Tipo | Notas |
|---|---|---|
| `id_log` | UUID | PK |
| `id_evento` | UUID | FK |
| `id_usuario` | UUID | FK (Quién disparó la exportación) |
| `tipo_reporte` | ENUM | `inscripciones`, `asistencia`, `agenda` |
| `formato` | ENUM | `pdf`, `csv` |
| `creado_el` | DATETIME | Timestamp automático |

---

## 6. Plan de Tareas / Tickets

| Ticket | Descripción | Depende de | Estimación |
|---|---|---|---|
| **T-5.1** | BD: Crear tabla `Audit_Reportes` para logs. | — | 1h |
| **T-5.2** | API: `GET /eventos/{id}/reportes/inscripciones` (Filtros + Paginación). | Mód. 1 y 2 | 4h |
| **T-5.3** | API: `GET /eventos/{id}/reportes/asistencia` (Joins + Agregación de KPIs). | Mód. 3 | 3h |
| **T-5.4** | API: `GET /eventos/{id}/reportes/agenda` (Listado ordenado). | Mód. 1 | 3h |
| **T-5.5** | Core: Servicio de exportación a CSV (UTF-8 + BOM). | T-5.2, T-5.3 | 3h |
| **T-5.6** | Core: Motor de renderizado PDF + Templates HTML/CSS base. | T-5.2 a T-5.4 | 5h |
| **T-5.7** | UI: Dashboard resumen (Maquetado de KPIs y links). | T-5.2, T-5.3 | 3h |
| **T-5.8** | API: Interceptor/Middleware para grabar el log en `Audit_Reportes`. | T-5.5, T-5.6 | 1h |
| **T-5.9** | QA: Cobertura de tests de exportación y validación de tenancy. | UI completa | 2h |

---

## 7. QA & Testing Strategy

### Unit / Security Tests
*   **Tenancy:** Request a `GET /reportes/inscripciones` con un usuario que no es dueño del evento → HTTP 403.
*   **Estado vacío:** Emitir agenda para evento sin cronograma → HTTP 422.
*   **Filtros:** Validar que el query builder aplique correctamente los rangos de fechas (inclusive/exclusive).

### Integration Tests
*   **Data Consistency:** Hacer match entre la sumatoria de nodos en el PDF de asistencia vs. un `COUNT()` real en la tabla `Acreditacion`.
*   **Cronología:** Verificar que el array de la agenda devuelva las actividades estrictamente ordenadas por `hora_inicio`.
*   **Encoding:** Exportar CSV con usuarios llamados "Niño" o "García" → Verificar integridad en parser estándar.

### Performance
*   **Load Test:** Gatillar el reporte de inscriptos para un evento *dummy* de 1000 usuarios. Evaluar consumo de RAM del generador de PDF y asegurar respuesta en `< 10s`.

### Smoke Test (E2E)
*   **Happy Path de Visualización:** Entrar al dashboard → Validar que el KPI de "Inscriptos" > 0 → Click en descargar CSV → Archivo descargado exitosamente con cabeceras correctas.