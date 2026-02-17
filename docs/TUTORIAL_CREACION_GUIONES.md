# 🎓 Tutorial: Tu Primer Guion en AIVideogen

Este tutorial te enseñará a "programar" tus propios videos usando el lenguaje **AVGL** (JSON). No necesitas ser programador, ¡es como llenar un formulario!

---

## 🛠️ Herramientas Necesarias

Aunque puedes usar el Bloc de Notas, te recomendamos encarecidamente:
1.  **[VS Code](https://code.visualstudio.com/)**: Es gratuito y te colorea el código para evitar errores.
2.  **AIVideogen**: Ya instalado (si no, mira el `README.md`).

---

## 🏁 Paso 1: El "Hola Mundo"

Vamos a crear un video de 10 segundos.

1.  Ve a la carpeta `aivideogen/examples/`.
2.  Copia el archivo `01_hello_world.json`.
3.  Pégalo en la carpeta `aivideogen/guiones/` (si no existe, créala).
4.  Renómbralo a `mi_primer_video.json`.

---

## ✍️ Paso 2: Editando el Guion

Abre `mi_primer_video.json` con VS Code. Verás algo así:

```json
{
    "title": "Hola Mundo AVGL",
    "blocks": [
        {
            "title": "Intro",
            "scenes": [
                {
                    "text": "Bienvenidos a AIVideogen.",
                    "asset": {
                        "type": "image",
                        "id": "media/assets/background.jpg"
                    }
                }
            ]
        }
    ]
}
```

### 🎯 Misión: Personalízalo
1.  Cambia `"Bienvenidos a AIVideogen."` por tu propio texto.
2.  Si tienes una imagen tuya, ponla en `aivideogen/media/assets/` y cambia `"media/assets/background.jpg"` por el nombre de tu archivo.

---

## 🏃 Paso 3: Generar el Video

Hay dos formas de "compilar" tu guion en un video:

### Opción A: El Asistente (Fácil)
1.  Haz doble clic en `Start_App.bat` (en la carpeta raíz).
2.  Sigue las instrucciones en pantalla.

### Opción B: Línea de Comandos (Rápido)
Abre una terminal en la carpeta principal y escribe:

```bash
# Windows
.\Start_App.bat --input "aivideogen/guiones/mi_primer_video.json"

# O si usas Python directo
python aivideogen/run_app.py --input "aivideogen/guiones/mi_primer_video.json"
```

El sistema empezará a:
1.  🗣️ Generar la voz (Text-to-Speech).
2.  🎵 Mezclar la música.
3.  🎞️ Renderizar el video con subtítulos karaoke.

---

## 🚀 Paso 4: Nivel Avanzado

¿Quieres efectos de cine? Mira el archivo `examples/02_advanced_features.json`. Aprenderás a usar:

- **`[TENSO]`**: Para cambiar la emoción de la voz.
- **Karaoke `[DYN]`**: Sincronización perfecta.
- **Zoom y Movimiento**: `"zoom": "1.0:1.5"`.

### Ejemplo de Escena Avanzada:
```json
{
    "title": "Acción",
    "text": "[EPICO]¡Esto es increíble![/EPICO]",
    "asset": {
        "id": "mi_imagen.jpg",
        "zoom": "1.0:1.3",     // Zoom lento hacia adentro
        "shake": true          // Temblor de cámara
    }
}
```

---

## 💡 Consejos de Oro

- **Guarda siempre en JSON**: Si te falta una coma `,` o una llave `}`, el sistema te avisará con un error. VS Code te ayuda a verlo en rojo.
- **Prueba con clips cortos**: Antes de hacer un documental de 10 minutos, haz pruebas de 15 segundos para ajustar los tiempos.
- **Usa la carpeta `examples`**: Es tu mejor "libro de recetas". Copia y pega lo que necesites.
