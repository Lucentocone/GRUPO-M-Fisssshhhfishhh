**SPEC – MÓDULO: GENERACIÓN DE CERTIFICADOS**
__________________________________________________________________________________________________

**1. OBJETIVO Y CONTEXTO**

**Objetivo**
Automatizar la creación, emisión y distribución de certificados digitales para los usuarios involucrados en un evento académico, reconociendo su participación según el rol desempeñado (organizador, participante o disertante).

**Contexto**
Al finalizar un evento académico, es un requisito indispensable entregar constancias de participación. Realizar este proceso de forma manual es propenso a errores e ineficiente. Este módulo permite configurar plantillas personalizadas por evento, generar los documentos en formato PDF de manera dinámica (individual o masiva) y proveer un mecanismo para su validación pública de autenticidad.

---

**2. HISTORIAS DE USUARIO Y CRITERIOS DE ACEPTACIÓN**

**HU 1 – Configurar plantilla de certificado**
Como organizador,  
quiero configurar una plantilla base para los certificados de mi evento,  
para que los documentos generados tengan la identidad visual y los datos correctos.

*Criterios de Aceptación:*
- El sistema debe permitir subir una imagen o diseño base (ej. membrete, firmas).
- Se deben poder definir variables dinámicas (Nombre del Usuario, Rol, Nombre del Evento, Fecha).
- Se debe poder visualizar una vista previa del certificado antes de confirmar la plantilla.
- Solo el organizador del evento puede modificar la plantilla.

**HU 2 – Generar y emitir certificados**
Como organizador,  
quiero generar y emitir los certificados para los usuarios de un evento,  
para oficializar su participación.

*Criterios de Aceptación:*
- El sistema debe permitir la generación masiva (para todos los asistentes) o individual.
- La generación debe asignar automáticamente el texto correspondiente según el rol del usuario (ej. "Por su participación como Disertante...").
- Se debe generar un código de verificación único para cada certificado emitido.
- El sistema debe notificar por correo electrónico a los usuarios una vez que su certificado esté listo.

**HU 3 – Descargar certificado propio**
Como usuario,  
quiero descargar mi certificado de un evento en el que participé,  
para tener un comprobante en mi poder.

*Criterios de Aceptación:*
- El usuario solo puede descargar certificados de eventos en los que tiene un rol asignado y confirmaron su asistencia.
- La descarga debe entregar un archivo en formato PDF.
- El certificado debe estar siempre disponible en el perfil del usuario.

**HU 4 – Validar autenticidad del certificado**
Como tercero (entidad externa o empleador),  
quiero validar un certificado ingresando su código único,  
para comprobar que el documento es legítimo y fue emitido por el sistema.

*Criterios de Aceptación:*
- El sistema debe contar con un endpoint o página pública de validación.
- Al ingresar un código válido o escanear el código QR impreso, el sistema debe mostrar los datos originales (Nombre, Evento, Rol, Fecha de emisión).
- Si el código no existe, debe mostrar un mensaje claro de "Certificado Inválido".

---

**3. REQUISITOS FUNCIONALES Y REGLAS DE NEGOCIO**

**Requisitos Funcionales**
- RF1: Gestión y carga de plantillas de certificados por evento.
- RF2: Generación dinámica de archivos PDF integrando datos del usuario, evento y rol.
- RF3: Generación de código único y código QR por cada certificado.
- RF4: Envío de notificaciones por email con el certificado adjunto o enlace de descarga.
- RF5: Portal público para la validación de certificados.

**Reglas de Negocio**
- RN1: Solo se puede emitir un certificado si el usuario tiene un rol válido y confirmado en el evento.
- RN2: Un usuario no puede tener más de un certificado por el mismo rol en un mismo evento.
- RN3: Los certificados emitidos son inmutables (no se pueden modificar; en caso de error, se debe anular y emitir uno nuevo).
- RN4: El código de validación debe ser único a nivel global del sistema, no solo del evento.

---

**4. RESTRICCIONES TÉCNICAS ESPECÍFICAS**

- Implementación de la generación de PDF utilizando una librería backend eficiente.
- La generación masiva de certificados debe manejarse mediante tareas asíncronas (background jobs/colas) para no bloquear la API.
- Almacenamiento seguro de los archivos PDF generados (ej. Amazon S3, almacenamiento local en servidor seguro) o generación "on the fly" basada en el registro para ahorrar espacio.
- Acceso público (sin autenticación) únicamente para el endpoint de validación de códigos.

---

**5. MODELO DE DATOS**

**Entidad: PlantillaCertificado**
- id (UUID)
- evento_id (UUID)
- url_imagen_fondo (String)
- configuracion_campos (JSON) → {posiciones X/Y para Nombre, Rol, Fecha, etc.}

**Entidad: Certificado**
- id (UUID)
- usuario_id (UUID)
- evento_id (UUID)
- rol_id (UUID)
- codigo_verificacion (String) → Unique
- url_pdf (String) → Opcional si se genera on the fly
- fecha_emision (DateTime)

---

**6. PLAN DE TAREAS**

1. Definir entidades `PlantillaCertificado` y `Certificado`.
2. Implementar servicio de generación de PDF e incrustación de variables/código QR.
3. Crear endpoints para la gestión de plantillas (subida y configuración).
4. Implementar endpoints y workers asíncronos para la emisión masiva/individual.
5. Crear endpoint para descarga de certificados por parte de los usuarios.
6. Desarrollar la página/endpoint público de validación de códigos.
7. Realizar pruebas integrales del proceso (Plantilla → Emisión → Descarga → Validación).

---

**7. ESTRATEGIA DE VERIFICACIÓN**

**Pruebas Unitarias**
- Validar la generación de códigos únicos y no repetibles.
- Validar que el motor de PDF posicione correctamente los textos configurados.
- Validar las reglas de negocio (ej. no emitir si no hay asistencia confirmada).

**Pruebas de Integración**
- Simular la emisión masiva para 100+ usuarios y verificar el rendimiento y uso de memoria.
- Flujo de guardado y posterior recuperación del certificado para descarga.

**Pruebas Funcionales**
- Generar un certificado de prueba, escanear el código QR y comprobar que dirige a la pantalla de validación exitosa.
- Intentar descargar un certificado desde una cuenta de usuario que no corresponde.

**Criterio de Aceptación General**
El módulo se considera completo cuando el organizador puede crear una plantilla y los usuarios pueden descargar un PDF válido, con sus datos correctos, que puede ser autenticado exitosamente por un tercero.
