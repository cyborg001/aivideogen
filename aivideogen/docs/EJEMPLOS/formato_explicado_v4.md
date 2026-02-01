# 📄 GUÍA DE FORMATO AVGL v4.0 (JSON)

El nuevo motor de video utiliza formato **JSON estándar**. Es más robusto, permite estructuras jerárquicas y es ideal para generar con IAs como ChatGPT o Claude.

## 🧱 Estructura Básica

Un archivo `.json` de AVGL tiene esta forma:

```json
{
  "title": "Título del Video",
  "voice": "es-ES-AlvaroNeural",
  "blocks": [
    {
      "title": "Bloque 1",
      "scenes": [
        {
          "title": "Escena 1",
          "text": "Texto que dirá la voz.",
          "assets": [ { "type": "imagen.png" } ]
        }
      ]
    }
  ]
}
```

## 🛠️ Propiedades Principales

### 1. Script (Raíz)
- `title`: Título interno del proyecto.
- `voice`: Voz por defecto para todo el video.
- `speed`: Velocidad de voz (1.0 = normal).
- `blocks`: Lista de bloques (capítulos).

### 2. Assets (Imágenes/Video)
Dentro de `"assets": []`:
- `type`: Nombre del archivo en la carpeta `assets` (ej: `foto.jpg`).
- `zoom`: "Inicio:Fin" (ej: `"1.0:1.3"`).
- `move`: "DIRECCION:Inicio:Fin" (ej: `"HOR:0:100"` o `"VER:10:90"`).
- `offset`: Segundos para iniciar (útil si hay múltiples assets, aunque normalmente es 1 por escena).
- `overlay`: Nombre del efecto superpuesto (ej: `"dust"`, `"grain"`).
- `fit`: `true` o `false`. Si es `true`, la imagen se ajusta sin recortar (barras negras).

### 3. Efectos de Sonido (SFX)
Dentro de `"sfx": []`:
- `type`: Nombre del archivo en `assets` (ej: `whoosh`).
- `volume`: 0.0 a 1.0.
- `offset`: Retraso en palabras (no segundos) desde el inicio del texto de la escena.

### 4. Texto y Emociones
Puedes usar etiquetas de emoción en el texto (Usa Estilos Nativos Azure):
- `"text": "[SUSPENSO] Algo se acerca... [/SUSPENSO]"`
- Etiquetas: `[EPICO]`, `[TENSO]`, `[SUSURRO]`, `[GRITANDO]`, `[SUSPENSO]`.
- Pausas: `[PAUSA:2.0]` (en segundos).

## 💡 Consejos
- **Una Escena = Una Imagen Pincipal:** Para cambiar de imagen, crea una nueva escena.
- **Validar JSON:** Usa un validador online o asegúrate de que no falten comas ni comillas.
