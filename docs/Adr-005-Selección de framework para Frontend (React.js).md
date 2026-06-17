# Título: ADR-005 Selección de framework para Frontend (React.js)

**Estado:** Aceptado  
**Fecha:** 2026-06-17  
**Decisores:** Wilmar Jesús Anchau, frannlo, Lucentocone  
**Relacionado:** #16, spec-frontend, project.md  

## Contexto
* **Qué problema se está resolviendo:** Se requiere definir la tecnología, arquitectura y herramientas del lado del cliente (Frontend) para la interfaz de usuario del sistema antes de comenzar el desarrollo del código.
* **Qué restricciones aplican (negocio, técnica, legal):** El equipo de desarrollo cuenta con tiempos acotados de entrega, se requiere una interfaz altamente interactiva de SPA (Single Page Application) y se debe garantizar una fácil integración mediante consumo de la API REST montada en Node.js.
* **Qué datos de proyecto sustentan la decisión:** El equipo posee conocimientos previos y experiencia práctica en el ecosistema de JavaScript, lo cual reduce drásticamente la curva de aprendizaje y optimiza la velocidad del desarrollo inicial.

## Decisión
Se decide adoptar **React.js** como la librería principal para la construcción de la interfaz de usuario del frontend.
* **Alcance:** Cubre la capa de presentación completa, el manejo del estado del cliente, el enrutamiento interno de la aplicación y el consumo de endpoints expuestos por el API Gateway. No cubre la lógica de negocio pesada, la cual queda delegada estrictamente en el backend.

## Alternativas consideradas
* **Opción A (React.js):**
    * *Pros:* Arquitectura basada en componentes reutilizables, ecosistema masivo, excelente documentación y rendimiento óptimo mediante Virtual DOM.
    * *Contras:* Requiere configurar herramientas adicionales de empaquetado (como Vite) y dependencias de terceros para resolver el enrutamiento (React Router).
* **Opción B (Angular):**
    * *Pros:* Framework robusto y completo "out-of-the-box" que provee soluciones integradas para formularios, rutas y peticiones HTTP.
    * *Contras:* Curva de aprendizaje empinada debido al uso obligatorio de TypeScript avanzado y una estructura de archivos rígida y pesada para el alcance actual del proyecto.

## Consecuencias
* **Beneficios esperados:** Desarrollo modular ágil a través de componentes reutilizables y consistencia visual en toda la aplicación.
* **Costos o riesgos que se aceptan:** Fatiga de dependencias en el ecosistema JavaScript por la necesidad de integrar librerías externas para el manejo de estados globales si el sistema escala.
* **Impacto en operación y equipo:** Curva de desarrollo fluida y distribución equitativa de tareas de maquetación dentro del repositorio.

## Plan de implementación
* Inicializar el proyecto frontend en el directorio correspondiente utilizando Vite y la plantilla de React.
* Configurar la estructura base de carpetas (`/components`, `/views`, `/services`) e instalar React Router para la navegación.

## Dependencias
* Node.js instalado en los entornos de desarrollo para la gestión de paquetes a través de npm o yarn.

## Métrica de éxito
* Interfaz de usuario fluida con tiempos de renderizado inferiores a los 200ms en transiciones de vistas locales.

## Triggers de revisión
* **Qué condiciones obligan a reabrir esta ADR:** Cambios drásticos en los requerimientos del cliente que exijan renderizado nativo en servidor (SSR) multilingüe ultra-complejo que React por sí solo dificulte.
* **Fecha sugerida de revisión:** 2026-09-15.