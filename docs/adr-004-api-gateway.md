# Título: ADR-004 Implementación de API Gateway para control de acceso y escalado

**Estado:** Propuesto
**Fecha:** 2026-06-16
**Decisores:** Cardozo Emanuel, Equipo de Desarrollo
**Relacionado:** Issue #[AQUÍ_VA_EL_NÚMERO_DE_TU_SEGUNDO_ISSUE]

## Contexto
- **Qué problema se está resolviendo:** Ante el crecimiento esperado del sistema, existe la necesidad de que ciertos módulos de la aplicación sean escalados horizontalmente. Además, se necesita un punto centralizado para controlar el acceso (autenticación) y limitar la tasa de peticiones (Rate Limiting) para evitar saturar las APIs.
- **Qué restricciones aplican:** Se debe minimizar la latencia introducida por agregar una capa extra de red.
- **Qué datos de proyecto sustentan la decisión:** Se proyecta un aumento de tráfico en el módulo de consultas, lo que requerirá levantar múltiples instancias del backend de forma dinámica.

## Decisión
Se decide implementar un API Gateway (utilizando Kong o un Nginx configurado como reverse proxy/gateway) como único punto de entrada para todas las peticiones de los clientes hacia el backend.
- **Alcance:** Cubre el enrutamiento de peticiones, terminación SSL, validación primaria de tokens JWT y rate limiting. No reemplaza la lógica de autorización detallada basada en roles, la cual seguirá en el backend.

## Alternativas consideradas
- **Opción A: Manejar el ruteo y rate limiting directamente en el código de la aplicación (Node.js).** 
  - Pros: Menos infraestructura que mantener, todo queda en el repositorio de código.
  - Contras: Consume recursos del servidor de aplicación, difícil de coordinar si hay múltiples instancias levantadas.
- **Opción B: Usar un servicio cloud gestionado (ej. AWS API Gateway).**
  - Pros: Cero mantenimiento de servidores, autoescalable.
  - Contras: Fuerte dependencia del proveedor (Vendor Lock-in) y costos potencialmente altos si el tráfico es masivo.

## Consecuencias
- **Beneficios esperados:** Mejor control sobre quién accede a qué módulo, facilidad para escalar módulos independientemente enviando el tráfico a diferentes instancias, mayor seguridad al no exponer los servidores backend a internet directamente.
- **Costos o riesgos que se aceptan:** Aumenta la complejidad de la infraestructura local y del entorno de desarrollo (requerirá Docker/Docker Compose para simularlo localmente).
- **Impacto en operación y equipo:** Los desarrolladores front-end solo se comunicarán con una única URL base, simplificando su configuración.

## Plan de implementación
- **Pasos mínimos para ejecutarla:**
  1. Escribir un archivo `docker-compose.yml` que incluya el servicio del API Gateway.
  2. Configurar las rutas básicas apuntando al servicio backend actual.
  3. Implementar el plugin de validación de JWT a nivel de Gateway.

## Dependencias
- Infraestructura compatible con contenedores (Docker).

## Métrica de éxito
- Reducción del 100% de peticiones no autenticadas llegando a los servidores backend (bloqueadas en el borde por el Gateway).

## Triggers de revisión
- **Qué condiciones obligan a reabrir esta ADR:** Si el API Gateway se convierte en un cuello de botella de rendimiento y añade más de 50ms de latencia promedio.
- **Fecha sugerida de revisión:** Antes de implementar la separación física de módulos en distintos servidores.