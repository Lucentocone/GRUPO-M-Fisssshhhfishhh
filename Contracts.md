# Contracts.md

## 1. Formato de respuestas API

### Éxito
{
  "status": "success",
  "data": {}
}

### Error
{
  "status": "error",
  "message": "Descripción del error"
}

---

## 2. Convenciones de datos

- Todos los IDs deben ser únicos
- Fechas en formato ISO 8601 (YYYY-MM-DD)
- Los textos no deben ser nulos

---

## 3. Validaciones generales

- Campos obligatorios no pueden estar vacíos
- Validar tipos de datos antes de procesar
- No permitir duplicados en registros clave

---

## 4. Seguridad (básico)

- Los usuarios deben estar autenticados para acciones privadas
- Roles deben ser verificados antes de ejecutar acciones
