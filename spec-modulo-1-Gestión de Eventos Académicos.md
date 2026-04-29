1. Objetivo y Contexto
Permitir a los organizadores dar de alta, modificar y publicar eventos académicos (cursos, congresos, charlas) para que sean visibles en la plataforma. Este módulo es el corazón del sistema, ya que provee la información que consumirán los demás módulos.

2. Historias de Usuario y Criterios de Aceptación
HU 1.1: Como organizador, quiero crear un evento para que los interesados puedan verlo.

Criterio: El evento debe tener obligatoriamente un título, tipo de evento y fecha de realización.

HU 1.2: Como visitante, quiero filtrar eventos por fecha (futuros/pasados) para encontrar los que me interesan.

Criterio: El sistema debe mostrar por defecto solo los eventos cuya fecha sea mayor o igual a la actual.

3. Requisitos Funcionales y Reglas de Negocio
RF: El sistema debe permitir cargar una descripción detallada y el cronograma del evento.

RN: No se pueden crear eventos con fechas de realización en el pasado.

RN: Si se define un cupo máximo, este debe ser un número entero positivo.

4. Restricciones Técnicas
Las imágenes de los eventos (banners) no deben superar los 2MB.

El filtrado de eventos debe realizarse del lado del servidor para optimizar el rendimiento.

5. Modelo de Datos
Entidad Evento: id_evento (PK), titulo, descripcion, fecha_evento, id_tipo_evento (FK), cupo_minimo, cupo_maximo, fecha_limite_inscripcion, estado (borrador/publicado).

6. Plan de Tareas
Diseñar la base de datos para eventos y tipos de eventos.

Desarrollar el formulario de carga con validaciones.

Implementar la lógica de filtrado de fechas en el backend.

7. Estrategia de Verificación
Prueba Unitaria: Validar que la función de "verificar fecha" rechace fechas anteriores al día de hoy.

Prueba de Humo: Crear un evento y verificar que aparezca correctamente en el listado público.
