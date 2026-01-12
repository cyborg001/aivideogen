# 📝 COMENTARIOS EN GUIONES

## ✅ **Nueva Funcionalidad Implementada** (v2.21.0)

Ahora puedes agregar comentarios y metadata en tus guiones usando `#`.

---

## 🎯 **Uso Básico**

### **Comentarios Simples**
Cualquier línea que empiece con `#` será **ignorada** por el generador:

```
# Este es un comentario - NO se procesa
# Puedes poner notas, versiones, fechas, etc.

Hook | imagen.png | ZOOM_IN | Texto del video |
```

---

## 🏷️ **Comentarios Especiales: HASHTAGS**

Extrae hashtags automáticamente para YouTube:

```
# HASHTAGS: #microondas #inventos #cocina #tecnologia #sabiasque

Hook | imagen.png | ZOOM_IN | Un chocolate derretido cambió la cocina para siempre | 1.5
El Accidente | melted_chocolate.png | VER:0:100 | Percy Spencer olvidó un chocolate en su bolsillo |
```

**Resultado**:
- Los hashtags se extraen automáticamente
- Se guardan en la base de datos
- Se usan en la descripción de YouTube
- **Reemplazan** los hashtags fijos si existen

---

## 🎵 **Comentarios Especiales: MÚSICA**

Sugiere música para el video:

```
# MÚSICA: Mysterious & Scientific, 120 BPM, Upbeat Discovery
```

**Resultado**:
- Se extrae y se muestra en los logs
- Útil para recordar qué música usar
- Se puede expandir en futuras versiones

---

## 📋 **Ejemplo Completo**

```
# ============================================
# GUION: Descubrimiento del Microondas
# FECHA: 2026-01-07
# AUTOR: Carlos Ramirez
# DURACIÓN ESTIMADA: 50 segundos
# ============================================

# HASHTAGS: #microondas #inventos #cocina #tecnologia #sabiasque #curiosidades
# MÚSICA: Upbeat Discovery, 120 BPM

# ESCENA 1: Hook impactante
Hook | scientist_lab.png | ZOOM_IN:1.0:1.3 | Un chocolate derretido cambió la cocina para siempre | 1.5

# ESCENA 2: El error
El Accidente | melted_chocolate.png | VER:0:100 | Percy Spencer olvidó un chocolate en su bolsillo mientras probaba un radar |

# NOTA: Usar transición suave aquí
La Intuición | microwave_invention.png | HOR:20:80 | En vez de molestarse, Spencer investigó por qué el chocolate se había derretido | 1.0

# ESCENA 4: Impacto
Resultado | modern_kitchen.png | ZOOM_OUT:1.4:1.0 | Hoy, el 90% de los hogares tienen un microondas gracias a ese error | 1.0

# CTA final
CTA | suscribete.mp4 | | Dale like y suscríbete para más descubrimientos increíbles | 2.0
```

---

## 🔍 **Cómo Funciona**

1. **Durante la validación** del guion:
   - Líneas con `#` se ignoran (no se procesan como escenas)
   - Se buscan `# HASHTAGS:` y se extraen los tags
   - Se busca `# MÚSICA:` y se extrae la sugerencia

2. **Durante la generación**:
   - Los hashtags se guardan en `project.script_hashtags`
   - Se muestran en los logs: `🏷️ Hashtags extraídos: #tag1 #tag2`

3. **Durante la subida a YouTube**:
   - Si existen hashtags del guion → se usan
   - Si NO existen → se usan hashtags fijos por defecto

---

## ⚙️ **Ventajas**

✅ **Documentación integrada**: Notas, fechas, versiones en el mismo archivo
✅ **Hashtags personalizados**: Cada video tiene sus propios tags relevantes
✅ **No se pierde información**: Todo queda en el guion
✅ **Flexible**: Puedes omitir hashtags y usar los fijos
✅ **Retrocompatible**: Guiones antiguos siguen funcionando

---

## 📊 **Casos de Uso**

### **1. Proyecto con múltiples versiones**
```
# VERSIÓN 1.0 - 2026-01-05
# VERSIÓN 1.1 - 2026-01-07 (corregido hook)

# HASHTAGS: #microondas #inventos
```

### **2. Notas de producción**
```
# TODO: Buscar mejor imagen para escena 3
# REVISAR: Audio de escena 2 muy bajo
```

### **3. Metadata completa**
```
# PROYECTO: Sabías Que
# TOPIC: Descubrimientos Por Error
# TARGET: YouTube Shorts
# HASHTAGS: #microondas #inventos #tecnologia
# MÚSICA: Mysterious & Scientific
```

---

**Última actualización**: 2026-01-07 (v2.21.0

)
