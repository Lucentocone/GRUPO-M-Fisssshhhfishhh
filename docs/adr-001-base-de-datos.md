# ADR-001 – Selección de motor de base de datos relacional (PostgreSQL)

**Estado:** Aceptado  
**Fecha:** 2026-04-10  
**Decisores:** Wilmar Jesús Anchau, Emanuel Cardozo, Franco (frannlo)  
**Relacionado:** Issue #2 · Project.md · Contracts.md · spec-modulo-5-Generacion-de-Reportes.md

---

## Contexto

### Qué problema se está resolviendo
El sistema de Gestión de Eventos Académicos necesita persistir y consultar múltiples
entidades relacionadas entre sí: eventos, participantes, inscripciones, roles, certificados
y registros de asistencia. Antes de redactar las specs de cada módulo fue necesario
definir qué motor de base de datos gestionaría esos datos.

El Módulo 5 (Generación de Reportes) es particularmente exigente en este aspecto:
requiere consultas complejas con múltiples JOINs (eventos ↔ inscripciones ↔
participantes ↔ asistencia) y exportación de resultados en PDF y CSV, lo que demanda
un motor que garantice integridad referencial y soporte eficiente de agregaciones.

### Restricciones que aplican
- **Negocio:** el sistema debe ser gratuito u open-source para minimizar costos operativos.
- **Técnica:** el equipo tiene experiencia previa con SQL estándar y bases de datos
  relacionales. No se dispone de experiencia con bases NoSQL en el equipo.
- **Legal:** los datos de participantes (DNI, email) deben almacenarse con garantías de
  integridad y consistencia transaccional (ACID).

### Datos del proyecto que sustentan la decisión
- El modelo de dominio definido en `Project.md` presenta relaciones muchos-a-muchos
  (Participante ↔ Evento a través de Inscripción) que se modelan naturalmente con tablas relacionales.
- Los 6 módulos requieren consultas cruzadas entre entidades, lo que favorece un motor relacional
  con soporte robusto de JOINs y transacciones.

---

## Decisión

Se adopta **PostgreSQL 16** como único motor de base de datos del sistema.

**Qué cubre esta decisión:**
- Toda la capa de persistencia del sistema (los 6 módulos).
- El esquema inicial de tablas (`db/init.sql`) y las migraciones futuras.
- El entorno de desarrollo local (vía Docker) y el entorno de producción.

**Qué NO cubre:**
- No define el ORM ni la capa de acceso a datos (eso es decisión del equipo de backend
  de cada módulo).
- No aplica a datos no estructurados eventuales (ej. archivos de certificados en PDF),
  que se almacenarán en el sistema de archivos o un servicio de almacenamiento externo.

---

## Alternativas consideradas

### Opción A: PostgreSQL (elegida)
- ✅ Open-source, sin costos de licencia.
- ✅ ACID completo: garantiza integridad en inscripciones concurrentes y control de cupos.
- ✅ Soporte nativo de tipos avanzados (UUID, JSONB, INET) útiles para auditoría (Módulo 5).
- ✅ Ecosistema maduro: drivers para Node.js (`pg`), Java (JDBC), Python (psycopg2).
- ✅ Imagen Docker oficial liviana (`postgres:16-alpine`).
- ❌ Más configuración inicial que SQLite para entornos locales simples.

### Opción B: MySQL / MariaDB
- ✅ Muy difundido, fácil de encontrar hosting gratuito.
- ✅ El equipo tiene alguna experiencia previa.
- ❌ Soporte de tipos avanzados más limitado (sin JSONB nativo, UUID menos ergonómico).
- ❌ Comportamiento histórico menos estricto con integridad referencial por defecto.
- ❌ Licencia dual en MySQL (puede generar fricción en el futuro).

### Opción C: SQLite
- ✅ Sin servidor, ideal para prototipado rápido.
- ✅ Cero configuración.
- ❌ No soporta concurrencia de escritura real: inviable para acreditación simultánea de
  participantes el día del evento (Módulo 2).
- ❌ Sin soporte de roles de usuario a nivel BD.
- ❌ No apto para producción en sistemas multi-usuario.

---

## Consecuencias

### Beneficios esperados
- Integridad referencial garantizada por constraints de FK en todas las relaciones del modelo.
- Las consultas de reportes (Módulo 5) pueden usar `GROUP BY`, `COUNT`, `AVG` y window
  functions de PostgreSQL para calcular KPIs sin lógica extra en el backend.
- El tipo `INET` permite registrar `ip_origen` en la tabla `audit_reportes` sin conversiones.
- Migraciones controladas con herramientas estándar (ej. Flyway, Liquibase).

### Costos o riesgos que se aceptan
- Requiere que Docker esté disponible en el entorno de desarrollo de todos los integrantes
  para levantar el servicio de BD localmente.
- Mayor overhead de configuración inicial respecto a SQLite.

### Impacto en operación y equipo
- Todos los módulos deben usar consultas parametrizadas (prepared statements) compatibles
  con PostgreSQL para prevenir inyección SQL (OWASP A03).
- El `docker-compose.yml` del proyecto define el servicio `db` con la imagen
  `postgres:16-alpine`, estandarizando la versión en todos los entornos.

---

## Plan de implementación

**Pasos mínimos:**
1. Definir el esquema inicial en `db/init.sql` con las tablas base del dominio.
2. Configurar el servicio `db` en `docker-compose.yml` con health check.
3. Cada módulo configura su cadena de conexión via la variable de entorno `DATABASE_URL`.
4. Las migraciones futuras se aplican con scripts numerados en `/db/migrations/`.

**Dependencias:**
- Docker y Docker Compose instalados en todos los entornos de desarrollo.
- Variable de entorno `DATABASE_URL` configurada en cada servicio de la aplicación.

**Métrica de éxito:**
- Los 6 módulos se conectan exitosamente a la BD en el entorno Docker local.
- El endpoint `GET /health/db` retorna `200 OK` con el timestamp del servidor PostgreSQL.

---

## Triggers de revisión

- Si el volumen de datos de inscriptos supera los **50.000 registros** y se detectan
  degradaciones de performance en los reportes del Módulo 5.
- Si surge el requerimiento de almacenar datos no estructurados en escala
  (ej. metadatos de eventos en formato libre), evaluar una estrategia híbrida con JSONB
  o un almacén complementario.
- **Fecha sugerida de revisión:** Junio 2027 (post-primera temporada de eventos reales).
