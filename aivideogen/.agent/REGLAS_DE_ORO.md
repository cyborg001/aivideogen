# 🔥 REGLAS DE ORO PARA BILL

## Git Workflow (CRÍTICO)

### ⚠️ REGLA #1: SIEMPRE TRABAJAR EN RAMAS
**NUNCA editar directamente en `master` cuando se trabaja en características nuevas o experimentales.**

**Flujo obligatorio:**
1. Crear rama: `git checkout -b feature/nombre-descriptivo`
2. Trabajar en la rama
3. Probar exhaustivamente
4. **Solo hacer merge a master cuando:**
   - El código esté probado
   - El usuario haya aprobado
   - No haya errores de sintaxis
5. Merge: `git checkout master && git merge feature/nombre-descriptivo`

**Ejemplos de nombres de rama:**
- `feature/avgl-v3-engine`
- `fix/performance-ken-burns`
- `feat/subtitle-system`

### Ventajas:
- ✅ Master siempre funcional
- ✅ Puedo descartar experimentos fallidos fácilmente
- ✅ Historial limpio y profesional
- ✅ Rollback seguro con `git checkout master`

---

## Servidor Django (CRÍTICO)

### ⚠️ REGLA #2: NUNCA AUTO-LANZAR EL SERVIDOR
**El usuario SIEMPRE lanza el servidor manualmente.**

**NUNCA hacer:**
- ❌ `run_command` con `python manage.py runserver`
- ❌ Lanzar el servidor "para ayudar"
- ❌ Asumir que el servidor debe estar corriendo

**SIEMPRE hacer:**
- ✅ Informar al usuario que puede lanzar el servidor
- ✅ Esperar a que el usuario lo lance por su cuenta
- ✅ Solo mencionar: "Puedes iniciar con: `python manage.py runserver`"

---

## Dependencias y Versiones (CRÍTICO)

### ⚠️ REGLA #3: VERIFICAR VERSIONES DE LIBRERÍAS
**NUNCA asumir que la API de una librería es la que conoces de memoria.**

**Antes de usar una librería externa compleja (como MoviePy, Pandas, etc.):**
1. **Verificar versión instalada:** Ejecutar `pip show <libreria>`
2. **Chequear "Breaking Changes":** Si la versión es reciente (ej: v2.x vs v1.x), buscar cambios de sintaxis.
3. **Introspección:** Si hay duda, crear un pequeño script con `dir()` para ver los métodos disponibles.
4. **No "alucinar" métodos:** Si un método falla (ej: `AttributeError`), no intentar "adivinar" el nombre. Verificarlo.

**Ejemplo del error a evitar:**
- Usar `.resize()` (v1.x) cuando la versión instalada es v2.x y usa `.resized()`.


