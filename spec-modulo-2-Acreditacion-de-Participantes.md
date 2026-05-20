# Spec – Módulo: Acreditación de Participantes

---

## 1. Objetivo y Contexto

### Objetivo
Gestionar el registro de asistencia de los participantes durante el evento. Este proceso asegura que solo quienes se presentaron efectivamente puedan recibir certificados y que los organizadores cuenten con datos reales para el análisis de métricas.

### Contexto
La inscripción previa no asegura la asistencia. Este módulo permite cerrar el flujo de usuario, permitiendo al organizador o al personal del evento validar la presencia de los inscriptos en tiempo real.
La acreditación se puede procesar de dos formas:
- Manual: Búsqueda rápida por nombre o documento.
- Agilizada: Escaneo del código QR enviado al participante tras su registro.
El estado de acreditación de cada participante es un dato crítico que consumen los módulos de Certificados y Reportes.

---

## 2. Historias de Usuario y Criterios de Aceptación

### HU 3.1: Acreditar participante manualmente
**Como** personal del evento,  
**quiero** buscar a un participante por nombre o DNI y marcar su asistencia,  
**para** registrar su presencia sin depender de tecnología de escaneo.

**Criterios de Aceptación:**
- El sistema muestra un campo de búsqueda que filtra en tiempo real sobre la lista de inscriptos del evento activo.
- La búsqueda puede realizarse por nombre completo (parcial) o por número de DNI exacto.
- Al seleccionar un participante, el sistema muestra sus datos (nombre, DNI, tipo de inscripción) y un botón "Acreditar".
- Al confirmar, el sistema registra la acreditación con timestamp y muestra un indicador visual de éxito (ej: fondo verde, ícono de check).
- Si el participante ya fue acreditado, el sistema lo indica claramente y no registra un duplicado.
- Solo usuarios con rol `organizador` o `staff` pueden acceder a esta funcionalidad.

### HU 3.2: Acreditar participante por código QR
**Como** personal del evento,  
**quiero** escanear el código QR del participante para acreditarlo,  
**para** agilizar el proceso de ingreso cuando hay mucha concurrencia.

**Criterios de Aceptación:**
- El sistema provee una vista de escaneo que activa la cámara del dispositivo.
- Al escanear un QR válido, el sistema muestra los datos del participante y confirma la acreditación automáticamente.
- Si el QR no corresponde a un inscripto del evento activo, el sistema muestra un mensaje de error descriptivo.
- Si el QR ya fue escaneado (participante ya acreditado), el sistema alerta al operador sin volver a registrar.
- El proceso completo (escaneo → confirmación) debe completarse en menos de 3 segundos en condiciones normales de red.

### HU 3.3: Consultar lista de acreditados
**Como** organizador,  
**quiero** ver en tiempo real cuántas personas ya fueron acreditadas y quiénes faltan,  
**para** conocer el estado de asistencia del evento en curso.

**Criterios de Aceptación:**
- El sistema muestra dos listas diferenciadas: "Acreditados" y "Pendientes de acreditación".
- Ambas listas muestran nombre completo, DNI y hora de acreditación (si aplica).
- El total acreditado y el total inscripto se muestran como contador en la cabecera de la vista (ej: "47 / 120 acreditados").
- La lista se actualiza automáticamente o con un botón de recarga manual.
- La vista es exportable a CSV para uso posterior.

---

## 3. Requisitos Funcionales y Reglas de Negocio

### Requisitos Funcionales
- **RF-3.1:** El sistema debe permitir la acreditación de participantes de forma manual (búsqueda por nombre/DNI).
- **RF-3.2:** El sistema debe permitir la acreditación mediante escaneo de código QR desde dispositivos móviles.
- **RF-3.3:** Cada acreditación debe registrar: `id_inscripcion`, `id_usuario_acreditador`, `fecha_hora_acreditacion`, `metodo` (manual/qr).
- **RF-3.4:** El sistema debe exponer un endpoint para consultar el estado de acreditación de todos los inscriptos de un evento.
- **RF-3.5:** El código QR debe ser generado al momento de confirmar la inscripción (módulo de Inscripción) y estar vinculado unívocamente a la inscripción.

### Reglas de Negocio
- **RN-3.1:** Un participante solo puede ser acreditado una vez por evento. Intentos duplicados deben ser rechazados con mensaje claro.
- **RN-3.2:** Solo puede realizarse la acreditación si el evento está en estado `publicado` y su fecha de realización es la actual o posterior en no más de 1 día (para cubrir eventos de varios días).
- **RN-3.3:** La acreditación no puede revertirse por la interfaz de usuario estándar; si se registró por error, solo un `organizador` puede anularla mediante una acción explícita con justificación registrada.
- **RN-3.4:** Los participantes con inscripción en estado `cancelado` no pueden ser acreditados.

---

## 4. Restricciones Técnicas Específicas de este Módulo

- **RT-3.1:** El escaneo de QR debe implementarse usando la API `getUserMedia` del navegador (sin app nativa), compatible con Chrome y Safari móvil. Se recomienda la librería `jsQR` o `html5-qrcode`.
- **RT-3.2:** El QR codifica únicamente el `id_inscripcion` (UUID v4). La validación completa ocurre en el backend; el frontend no debe exponer datos sensibles en el QR.
- **RT-3.3:** Las operaciones de acreditación deben ser atómicas (transacción de base de datos) para evitar acreditaciones duplicadas por concurrencia (ej: dos dispositivos escaneando el mismo QR simultáneamente).
- **RT-3.4:** El endpoint de acreditación debe responder en menos de 500ms bajo carga normal para no generar cuellos de botella en el ingreso.
- **RT-3.5:** La vista de lista de acreditados con filtrado en tiempo real debe manejar listas de hasta 1000 inscriptos sin degradación visible del rendimiento.
- **RT-3.6:** Todos los endpoints de este módulo requieren autenticación JWT y verificación de rol (`organizador` o `staff`). Ver `Contracts.md` para formato de respuestas.

---

## 5. Modelo de Datos de este Módulo

### Entidad: `Acreditacion`
| Campo | Tipo | Restricción | Descripción |
|---|---|---|---|
| `id_acreditacion` | UUID | PK | Identificador único |
| `id_inscripcion` | UUID | FK → Inscripcion, UNIQUE | Una inscripción = una acreditación |
| `id_usuario_acreditador` | UUID | FK → Usuario | Staff que realizó la acreditación |
| `fecha_hora_acreditacion` | DATETIME | NOT NULL | Timestamp del registro (ISO 8601) |
| `metodo` | ENUM | NOT NULL | Valores: `manual`, `qr` |
| `anulada` | BOOLEAN | DEFAULT FALSE | Si fue anulada por error |
| `motivo_anulacion` | TEXT | NULLABLE | Obligatorio si `anulada = true` |

## 6. Plan de Tareas

| # | Tarea | Dependencia | Estimación |
|---|---|---|---|
| T-3.1 | Agregar columna `qr_token` (UUID) a la tabla `Inscripcion` y generar token al crear inscripción | Módulo 2 completado | 2h |
| T-3.2 | Crear tabla `Acreditacion` con sus restricciones e índices | T-3.1 | 1h |
| T-3.3 | Implementar `POST /acreditaciones` (acreditación manual y por QR) con validaciones y control de concurrencia | T-3.2 | 4h |
| T-3.4 | Implementar `GET /eventos/{id}/acreditaciones` (lista con estado) | T-3.2 | 2h |
| T-3.5 | Implementar `PATCH /acreditaciones/{id}/anular` (solo organizador, con motivo) | T-3.3 | 2h |
| T-3.6 | Desarrollar vista de acreditación manual (búsqueda + botón acreditar) | T-3.3 | 3h |
| T-3.7 | Desarrollar vista de escaneo QR (integración jsQR / html5-qrcode) | T-3.3 | 4h |
| T-3.8 | Desarrollar vista de lista de acreditados con contadores y exportación CSV | T-3.4 | 3h |
| T-3.9 | Pruebas de integración y carga | T-3.6, T-3.7, T-3.8 | 3h |
| T3.10 | Implementar búsqueda en tiempo real por nombre/DNI (frontend) | T3.1 | 2h |


---

## 7. Estrategia de Verificación

### Pruebas Unitarias
- **PU-3.1:** Verificar que el servicio de acreditación rechace un `id_inscripcion` ya acreditado y retorne error con código HTTP 409.
- **PU-3.2:** Verificar que el servicio rechace acreditaciones para inscripciones con estado `cancelado`.
- **PU-3.3:** Verificar que un QR con UUID inválido o inexistente retorne HTTP 404.

### Pruebas de Concurrencia
- **PC-3.1:** Simular 10 solicitudes simultáneas de acreditación del mismo `id_inscripcion` y verificar que solo 1 sea exitosa (HTTP 200) y las restantes reciban HTTP 409. Herramienta sugerida: Apache JMeter o k6.

### Pruebas de Integración
- **PI-3.1:** Crear inscripción → verificar generación de `qr_token` → acreditar por QR → verificar registro en `Acreditacion` → verificar que el módulo de Reportes refleje el cambio de asistencia.
- **PI-3.2:** Acreditar manualmente → anular acreditación con motivo → verificar que el participante vuelva a aparecer como "Pendiente".

### Prueba de Humo (Smoke Test)
- **PS-3.1:** Flujo completo de punta a punta: inscribir un participante de prueba → abrir vista de acreditación → buscarlo por nombre → acreditarlo → verificar que aparece en la lista de acreditados con timestamp correcto.

### Criterio de Aceptación General
Todos los criterios de aceptación de las HU 3.1, 3.2 y 3.3 deben estar verificados antes de considerar el módulo como completo.
