1. Objetivo y Contexto
Gestionar la vinculación de los participantes con los eventos. Este módulo controla que las inscripciones sean válidas según las reglas de negocio de tiempo y capacidad definidas en el módulo de Eventos.

2. Historias de Usuario y Criterios de Aceptación
HU 2.1: Como participante, quiero inscribirme a un evento para asegurar mi lugar.

Criterio: El sistema debe confirmar la inscripción solo si hay cupo disponible y la fecha límite no ha pasado.

HU 2.2: Como personal del evento, quiero inscribir a un participante manualmente.

Criterio: El personal debe poder saltar la restricción de "fecha límite" si fuera necesario (cortesía).
       
3. Requisitos Funcionales y Reglas de Negocio
RF: El sistema debe enviar un mail automático de confirmación al usuario tras inscribirse.

RN: Un usuario no puede estar inscrito dos veces en el mismo evento.

RN: Si se alcanza el cupo_maximo, el sistema debe marcar el evento como "Agotado".

4. Restricciones Técnicas
Uso de transacciones de base de datos (ACID) para asegurar que no se sobrepase el cupo si dos personas se inscriben exactamente al mismo tiempo.

5. Modelo de Datos
Entidad Inscripcion: id_inscripcion (PK), id_evento (FK), id_usuario (FK), fecha_inscripcion, modalidad (autónoma/staff).

6. Plan de Tareas
Crear el endpoint POST /eventos/{id}/inscribir.

Implementar el control de concurrencia para el cupo máximo.

Desarrollar el servicio de notificaciones por email.

7. Estrategia de Verificación
Prueba de Carga: Simular 10 inscripciones simultáneas para un evento con solo 5 cupos y verificar que solo 5 sean exitosas.

Prueba de Integración: Verificar que al realizar una inscripción, el contador de cupos del evento se actualice correctamente.
