# Título: ADR-006 Implementación de Circuit Breaker ante fallas en APIs Externas

**Estado:** Propuesto  
**Fecha:** 2026-06-17  
**Decisores:** Wilmar Jesús Anchau, frannlo, Lucentocone  
**Relacionado:** #17, spec-error-handling   

## Contexto
* **Qué problema se está resolviendo:** El sistema interactúa con APIs externas (como procesadores de pagos o servicios de geolocalización). Ante caídas, intermitencias o latencias altas en dichos proveedores, nuestro backend degrada su rendimiento, bloquea hilos de ejecución y propaga errores no controlados a los usuarios.
* **Qué restricciones aplican (negocio, técnica, legal):** No tenemos control sobre la disponibilidad ni los tiempos de respuesta de los servicios de terceros (restricción técnica externa).
* **Qué datos de proyecto sustentan la decisión:** Las pruebas de integración iniciales arrojaron que un fallo en la API externa causa solicitudes en cascada colgadas, elevando el tiempo de respuesta general del backend a más de 10 segundos antes de fallar por timeout.

## Decisión
Se decide implementar el patrón **Circuit Breaker (Disyuntor)** utilizando la librería *Opossum* en el entorno de Node.js para aislar las llamadas hacia APIs de terceros.
* **Alcance:** Aplica a todas las solicitudes salientes orientadas a servicios externos integrados en el sistema. No abarca las consultas locales dirigidas a nuestra base de datos PostgreSQL ni a la caché de Redis.

## Alternativas consideradas
* **Opción A (Patrón Circuit Breaker):**
    * *Pros:* Evita llamadas innecesarias a servicios caídos, permite definir respuestas de fallback (degradación elegante de la interfaz) y da tiempo al servicio externo para recuperarse.
    * *Contras:* Introduce complejidad adicional en la arquitectura de backend y requiere configurar umbrales precisos de fallo.
* **Opción B (Reintentos directos con lógica lineal - Retry Policy):**
    * *Pros:* Es extremadamente sencilla de programar con bucles `for/while` tradicionales.
    * *Contras:* Empeora el escenario (efecto "bando de la muerte") al saturar aún más al proveedor externo intermitente y retrasar la respuesta final al cliente.

## Consecuencias
* **Beneficios esperados:** Resiliencia y tolerancia a fallas del backend. Si un servicio externo cae, la app responde de inmediato con una acción alternativa o un error controlado sin colgar el servidor.
* **Costos o riesgos que se aceptan:** Sobrecarga mínima de código para monitorear los estados del circuito (Abierto, Cerrado, Semi-abierto).
* **Impacto en operación y equipo:** Obliga al equipo a definir respuestas estáticas o flujos de contingencia para cada servicio externo fallido.

## Plan de implementación
* Instalar e integrar la librería de manejo de disyuntores en los servicios de comunicación externa del backend.
* Configurar un umbral de error del 50% y un timeout de 3 segundos como parámetros por defecto para abrir el circuito.

## Dependencias
* Estructura modular de Backend en Node.js (establecida en la ADR-003).

## Métrica de éxito
* El 100% de las solicitudes a APIs externas caídas deben ser interrumpidas y devueltas con un fallback controlado en menos de 500ms, protegiendo la estabilidad del backend.

## Triggers de revisión
* **Qué condiciones obligan a reabrir esta ADR:** Si la tasa de falsos positivos en la apertura del circuito afecta operaciones de negocio críticas que toleren esperas más largas.
* **Fecha sugerida de revisión:** 2026-08-01.