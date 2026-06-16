# Título: ADR-003 Selección de lenguaje y framework para Backend (Node.js y Express)

**Estado:** Aceptado
**Fecha:** 2026-06-16
**Decisores:** Cardozo Emanuel, Equipo de Desarrollo
**Relacionado:** Issue #[AQUÍ_VA_EL_NÚMERO_DE_TU_PRIMER_ISSUE]

## Contexto
- **Qué problema se está resolviendo:** Se necesitaba definir la tecnología principal para desarrollar la lógica de negocio y exponer la API REST del sistema, antes de comenzar con la redacción de las especificaciones y el project.md.
- **Qué restricciones aplican:** El equipo cuenta con conocimientos previos en JavaScript/TypeScript. Se requiere un desarrollo ágil y un ecosistema amplio de librerías para integraciones rápidas.
- **Qué datos de proyecto sustentan la decisión:** La arquitectura planeada se basa en microservicios/servicios distribuidos ligeros que requieren alta concurrencia de entrada/salida (I/O) sin un consumo excesivo de CPU.

## Decisión
Se decide utilizar Node.js como entorno de ejecución y Express.js como framework web para el desarrollo del backend.
- **Alcance:** Esto cubre el desarrollo de todos los endpoints de la API, el enrutamiento y la lógica de controladores. No cubre el desarrollo del frontend ni los procesos asíncronos pesados en background.

## Alternativas consideradas
- **Opción A: Python con Django.** 
  - Pros: Excelente ORM integrado, estructura muy robusta.
  - Contras: Mayor curva de aprendizaje para el equipo, más "pesado" para microservicios simples.
- **Opción B: Java con Spring Boot.**
  - Pros: Fuertemente tipado, extremadamente seguro y escalable a nivel corporativo.
  - Contras: Mayor tiempo de configuración inicial (boilerplate) y mayor consumo de memoria RAM.

## Consecuencias
- **Beneficios esperados:** Desarrollo rápido, unificación del lenguaje si se usa React/Angular en el frontend (JavaScript en todo el stack), excelente manejo de peticiones concurrentes.
- **Costos o riesgos que se aceptan:** Node.js es de un solo hilo (single-threaded), por lo que si a futuro hay tareas que requieran procesamiento intensivo de CPU, podrían bloquear el event loop.
- **Impacto en operación y equipo:** El equipo requerirá estandarizar el uso de middlewares para manejo de errores de forma consistente.

## Plan de implementación
- **Pasos mínimos para ejecutarla:** 
  1. Inicializar el proyecto con `npm init`.
  2. Instalar dependencias base (`express`, `cors`, `dotenv`).
  3. Configurar la estructura de carpetas (routes, controllers, services).

## Dependencias
- Servidor con entorno de ejecución Node.js instalado (v18 o superior).

## Métrica de éxito
- Lograr levantar el primer endpoint (Health Check) en menos de 1 hora de configuración y mantener un tiempo de respuesta menor a 200ms en consultas sin carga.

## Triggers de revisión
- **Qué condiciones obligan a reabrir esta ADR:** Si el sistema comienza a requerir algoritmos de procesamiento de datos muy pesados (CPU-bound) que degraden el rendimiento de la API.
- **Fecha sugerida de revisión:** Revisión trimestral tras el lanzamiento a producción.