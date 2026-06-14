# ADR-002 – Incorporación de Redis como caché para el Módulo de Generación de Reportes

**Estado:** Aceptado  
**Fecha:** 2026-06-14  
**Decisores:** Franco (frannlo)  
**Relacionado:** Issue #3 · spec-modulo-5-Generacion-de-Reportes.md · R5 (análisis de riesgos TP4)

---

## Contexto

### Qué problema se está resolviendo
Durante las pruebas de carga del Módulo 5 (Generación de Reportes) se identificó que
las consultas de exportación — especialmente el **reporte de inscriptos** y el
**dashboard de KPIs** — presentan latencia alta cuando el evento supera los 300
participantes registrados.

El problema concreto es que cada vez que un organizador solicita un reporte, el backend
ejecuta consultas pesadas con múltiples JOINs sobre las tablas `eventos`, `inscripciones`,
`participantes` y `audit_reportes`. Si varios organizadores generan reportes en simultáneo
(situación típica horas antes de un congreso), la base de datos queda sobrecargada.

Esto impacta directamente en la SLA definida en la HU 5.1:
> *"Generación en < 10 segundos para payloads de hasta 500 registros"*

### Restricciones que aplican
- **Negocio:** los reportes de inscriptos no cambian en tiempo real cada segundo —
  se actualizan cuando alguien se inscribe o cancela. Un reporte "fresco" de hace
  60 segundos es aceptable para fines de logística.
- **Técnica:** el stack actual (Node.js + Express + PostgreSQL) no incluye ninguna
  capa de caché. Agregar una solución in-process (variables globales de Node.js)
  no escalaría si en el futuro el servicio se despliega en múltiples instancias.
- **Operativa:** el entorno de desarrollo ya usa Docker Compose, lo que simplifica
  agregar Redis como un servicio adicional sin fricción.

### Datos del proyecto que sustentan la decisión
- La HU 5.1 especifica un SLA de `< 10s` para 500 registros, actualmente no cumplido
  en escenarios de carga concurrente.
- El análisis de riesgos (TP4, R5) identificó "inconsistencias y problemas de performance
  en el módulo de Generación de Reportes" como riesgo de producto.
- Los reportes de inscriptos y asistencia son de solo-lectura para los organizadores:
  ninguna acción dentro del módulo 5 modifica los datos fuente, lo que hace que la caché
  sea segura de aplicar sin riesgo de datos desactualizados en escrituras.

---

## Decisión

Se incorpora **Redis 7** como capa de caché distribuida para el Módulo 5, aplicada
exclusivamente a los endpoints de consulta de reportes.

**Qué cubre esta decisión:**
- Caché de resultados de los endpoints:
  - `GET /api/reportes/:eventoId/inscripciones`
  - `GET /api/reportes/:eventoId/asistencia`
  - `GET /api/reportes/:eventoId/dashboard`
- TTL (Time To Live) de **60 segundos** para reportes de inscriptos y dashboard.
- TTL de **300 segundos** para el reporte de asistencia (post-evento, cambia con menor frecuencia).
- Invalidación activa de caché cuando se registra una nueva inscripción o acreditación
  (evento disparado por los módulos 1 y 2 respectivamente).

**Qué NO cubre:**
- No aplica a la exportación de archivos PDF/CSV (estos se generan siempre frescos
  bajo demanda para garantizar exactitud en el documento descargado).
- No reemplaza ni modifica la base de datos PostgreSQL.
- No aplica a otros módulos del sistema en esta versión.

---

## Alternativas consideradas

### Opción A: Redis (elegida)
- ✅ Caché distribuida: funciona correctamente si el servicio se escala horizontalmente.
- ✅ Imagen Docker oficial (`redis:7-alpine`), integración trivial en `docker-compose.yml`.
- ✅ Soporte de TTL nativo por clave: invalidación automática sin código extra.
- ✅ Muy bajo uso de memoria para el volumen de datos de reportes (JSON de KBs).
- ✅ Ampliamente adoptado: el equipo puede encontrar documentación y ejemplos fácilmente.
- ❌ Agrega un servicio más al stack (mayor superficie operativa).
- ❌ Requiere lógica de invalidación activa al modificar datos fuente.

### Opción B: Caché en memoria de Node.js (ej. `node-cache`)
- ✅ Sin dependencias externas, cero configuración.
- ✅ Latencia de acceso mínima (en proceso).
- ❌ La caché se pierde si el proceso de Node.js se reinicia.
- ❌ No compartida entre instancias: si el servicio escala a 2 contenedores,
  cada uno tiene su propia caché desincronizada.
- ❌ No apta para un entorno de producción serio.

### Opción C: Caché a nivel de base de datos (materialized views de PostgreSQL)
- ✅ Sin componentes externos: todo en PostgreSQL.
- ✅ Las vistas materializadas pueden refrescarse con `REFRESH MATERIALIZED VIEW`.
- ❌ El refresco es manual o requiere triggers complejos en la BD.
- ❌ No reduce la carga de conexiones a la BD en escenarios de alta concurrencia.
- ❌ Agrega complejidad al esquema de datos.

---

## Consecuencias

### Beneficios esperados
- Las consultas de reportes frecuentes (dashboard, inscriptos) se resuelven desde Redis
  en `< 5ms`, cumpliendo ampliamente el SLA de `< 10s`.
- La base de datos PostgreSQL queda descargada de consultas repetitivas, mejorando
  la performance global del sistema durante picos de uso.
- La arquitectura queda preparada para escalar el servicio de reportes horizontalmente
  sin problemas de consistencia de caché.

### Costos o riesgos que se aceptan
- **Datos levemente desactualizados:** un organizador podría ver un reporte de inscriptos
  con hasta 60 segundos de retraso. Se acepta porque el TTL es bajo y el caso de uso
  (logística del evento) no requiere precisión al segundo.
- **Complejidad operativa:** se suma un servicio más a monitorear en producción.
- **Riesgo de cache stampede:** si muchos usuarios solicitan el mismo reporte cuando
  el TTL expira simultáneamente. Mitigación: implementar "probabilistic early expiration"
  o un lock distribuido básico.

### Impacto en operación y equipo
- Se agrega el servicio `redis` al `docker-compose.yml`.
- El backend del Módulo 5 requiere el paquete `ioredis` para interactuar con Redis.
- Se debe documentar la estrategia de invalidación de caché para los desarrolladores
  de los módulos 1 (Inscripción) y 2 (Acreditación), ya que sus operaciones de escritura
  deben disparar la invalidación de las claves de caché del módulo 5.

---

## Plan de implementación

**Pasos mínimos:**
1. Agregar el servicio `redis` en `docker-compose.yml`:
   ```yaml
   redis:
     image: redis:7-alpine
     container_name: eventos-academicos-redis
     ports:
       - "6379:6379"
     networks:
       - eventos-network
   ```
2. Instalar el cliente en el servicio de app: `npm install ioredis`.
3. Crear el módulo `src/cache/redisClient.js` con la configuración de conexión.
4. Envolver los handlers de los endpoints de reportes con lógica de
   "leer de caché → si miss → consultar BD → guardar en caché".
5. Agregar variable de entorno `REDIS_URL=redis://redis:6379` en `docker-compose.yml`.
6. Implementar invalidación: cuando el Módulo 1 registra una inscripción,
   llamar a `redis.del(`reporte:${eventoId}:*`)`.

**Dependencias:**
- Servicio Redis 7 disponible en la red Docker interna.
- Coordinación con los equipos de Módulo 1 y Módulo 2 para implementar
  la invalidación de caché en sus endpoints de escritura.

**Métrica de éxito:**
- El endpoint `GET /api/reportes/:eventoId/dashboard` responde en `< 100ms`
  en la segunda solicitud (cache hit) para eventos con hasta 500 inscriptos.
- La tasa de cache hit rate es `> 80%` durante las 2 horas previas al inicio de un evento
  (período de mayor consulta de reportes).

---

## Triggers de revisión

- Si el número de eventos simultáneos supera **10 por día**, revisar si el TTL
  de 60s sigue siendo adecuado o si conviene reducirlo.
- Si se detectan inconsistencias de datos reportadas por organizadores relacionadas
  con la caché, evaluar reducir el TTL o migrar a invalidación 100% event-driven.
- Si Redis consume más del **10% de la RAM disponible** en el servidor de producción,
  revisar la política de evicción (`maxmemory-policy allkeys-lru`).
- **Fecha sugerida de revisión:** Diciembre 2026, tras la primera temporada de
  congresos con el sistema en producción.
