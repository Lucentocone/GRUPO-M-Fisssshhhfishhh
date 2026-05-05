
# SPEC – MÓDULO: GESTIÓN DE ROLES

## 1. OBJETIVO Y CONTEXTO

### Objetivo  
Administrar los roles de los usuarios dentro de cada evento académico, definiendo sus permisos y responsabilidades según su participación como organizador, participante o disertante.

### Contexto  
En un evento académico, los usuarios pueden desempeñar diferentes funciones. Este módulo permite asignar, modificar y consultar roles asociados a un usuario dentro de un evento específico.

Los roles son fundamentales para controlar el acceso a funcionalidades del sistema y garantizar que cada usuario pueda realizar únicamente las acciones permitidas.

---

## 2. HISTORIAS DE USUARIO Y CRITERIOS DE ACEPTACIÓN

### HU 1 – Asignar rol a usuario  
Como organizador,  
quiero asignar uno o más roles a un usuario en un evento,  
para definir su participación.

Criterios de Aceptación:  
# El sistema debe permitir seleccionar un usuario inscripto en el evento  
# Se deben poder asignar los roles: organizador, participante, disertante  
# Un usuario puede tener más de un rol en el mismo evento  
# La asignación debe persistirse correctamente  
# Solo usuarios con rol organizador pueden asignar roles  

---

### HU 2 – Consultar roles de un usuario  
Como usuario,  
quiero visualizar mis roles en un evento,  
para conocer mis permisos dentro del sistema.

Criterios de Aceptación:  
# El sistema debe mostrar todos los roles asociados al usuario en el evento  
# Si el usuario no tiene roles asignados, debe indicarse explícitamente  
# La información debe estar disponible al acceder al detalle del evento  

---

### HU 3 – Modificar roles  
Como organizador,  
quiero modificar los roles de un usuario,  
para actualizar su participación en el evento.

Criterios de Aceptación:  
# Se deben poder agregar o eliminar roles existentes  
# Los cambios deben reflejarse inmediatamente  
# No se deben permitir roles inválidos  
# Solo organizadores pueden realizar modificaciones  

---

### HU 4 – Validar permisos según rol  
Como sistema,  
quiero validar las acciones de los usuarios según su rol,  
para garantizar seguridad y control de acceso.

Criterios de Aceptación:  
# Un participante no puede gestionar eventos  
# Un disertante puede estar asociado a actividades específicas  
# Un organizador tiene control total sobre el evento  
# El sistema debe bloquear acciones no permitidas  

---

## 3. REQUISITOS FUNCIONALES Y REGLAS DE NEGOCIO

### Requisitos Funcionales  

# RF1: Asignar roles a usuarios dentro de un evento  
# RF2: Consultar roles de un usuario  
# RF3: Modificar roles existentes  
# RF4: Validar permisos en base a roles  
# RF5: Asociar roles a eventos específicos  

---

### Reglas de Negocio  

# RN1: Un usuario puede tener múltiples roles en un mismo evento  
# RN2: Todo evento debe tener al menos un organizador  
# RN3: No se puede eliminar el único organizador de un evento  
# RN4: Los roles válidos son: organizador, participante, disertante  
# RN5: Los permisos del sistema dependen del rol asignado  
# RN6: La asignación de roles es específica por evento (no global)  

---

## 4. RESTRICCIONES TÉCNICAS ESPECÍFICAS DE ESTE MÓDULO

# Implementación mediante API REST  
# Endpoints protegidos con autenticación  
# Validación de roles en backend  
# Uso de identificadores únicos para usuarios y eventos  
# El sistema debe permitir agregar nuevos roles en el futuro sin afectar la estructura actual  

---

## 5. MODELO DE DATOS DE ESTE MÓDULO

Entidad: Usuario  
# id (UUID)  
# nombre (String)  
# email (String)  

Entidad: Evento  
# id (UUID)  
# nombre (String)  

Entidad: Rol  
# id (UUID)  
# nombre (String) → {organizador, participante, disertante}  

Entidad: UsuarioEventoRol  
# id (UUID)  
# usuario_id (UUID)  
# evento_id (UUID)  
# rol_id (UUID)  

---

## 6. PLAN DE TAREAS

# Definir entidad Rol  
# Crear relación entre Usuario, Evento y Rol  
# Implementar endpoint para asignación de roles  
# Implementar consulta de roles por usuario  
# Implementar modificación de roles  
# Implementar validación de permisos  
# Realizar pruebas del módulo  

---

## 7. ESTRATEGIA DE VERIFICACIÓN

### Pruebas Unitarias  
# Validar asignación correcta de roles  
# Validar que no se permitan roles inválidos  
# Validar reglas de negocio (mínimo un organizador)  

### Pruebas de Integración  
# Flujo completo: asignar → consultar → modificar roles  
# Validación de persistencia de datos  

### Pruebas Funcionales  
# Visualización de roles por usuario  
# Restricción de acciones según rol  
# Modificación de roles desde interfaz  

### Criterio de Aceptación General  
El módulo se considera completo cuando todas las historias de usuario cumplen sus criterios de aceptación y las reglas de negocio se validan correctamente.
