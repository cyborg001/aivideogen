# 📜 MANUAL: AVGL (AI Video Generation Language) v3.0

Bienvenido al lenguaje de edición **AVGL**. Este sistema sustituye el formato de columnas por un lenguaje de marcado estructurado que otorga control total sobre cada milisegundo del video.

## 🏗️ Estructura Jerárquica (v3.0 Plus Plus)
AVGL utiliza ahora una estructura de "Capas de Cebolla" para un control organizacional máximo:

1.  **Raíz `<avgl title="...">`**: Contenedor maestro.
    - **Efecto**: El atributo `title` actualiza automáticamente el título del proyecto en la base de datos de la Web App.
2.  **Partes `<bloque title="..." music="...">`**: Agrupadores narrativos (Bloques).
    - **Efecto**: La música definida en el bloque se hereda a todas las escenas interiores. Cambiar de bloque cambia la música.
3.  **Capítulos `<scene title="...">`**: Unidades de acción e imagen.

```xml
<avgl title="Título Maestro">
  <bloque title="Parte 1" music="pista_1">
    <scene title="Capítulo 1">
      <asset type="foto.png" />
      Narración de la escena...
    </scene>
  </bloque>
</avgl>
```

## 🏷️ Etiquetas de Evento In-Line

### 🔊 Audio y Efectos
- `<sfx type="nombre" volume="0.5" />`: Dispara un efecto de sonido instantáneo en ese punto exacto del texto.
- `<ambient state="start" type="factory" volume="0.1" />`: Inicia un sonido de ambiente en bucle (texturas sonoras).
- `<ambient state="stop" />`: Detiene el ambiente actual.
- `<bloque music="nombre_pista" volume="0.2" />`: Define una "Parte" o "Capítulo" del video con su propia música de fondo.
  - **Uso**: Ideal para separar un video en secciones (ej: Intro vs Desarrollo).
  - **Efecto**: Cambia la música y desactiva la selección global de la App para evitar solapamientos.

### 🎙️ Capa de Abstracción de Voz
Bill actúa como traductor universal para que el guion sea compatible con múltiples motores (Edge TTS, ElevenLabs).
- `<voice name="es-MX-JorgeNeural"> ... </voice>`: Cambia el narrador actual.
- **Etiquetas de Emoción (Abstractas)**:
  - `[TENSO] texto [/TENSO]`: Bill lo traduce a SSML (pitch bajo, velocidad lenta) o envía el parámetro de estilo a ElevenLabs.
  - `[EPICO] texto [/EPICO]`: Aumenta el volumen y la intensidad.

### ⏱️ Control de Tiempo
- `<pause duration="1.5" />`: Introduce un silencio dramático. Durante la pausa, los efectos visuales y el ambiente continúan.

### 🎬 Disparadores Visuales e In-Line
- `<asset type="imagen.png" zoom="1.0:1.3" move="HOR:0:100" overlay="grain" />`: Cambia el activo y aplica efectos.
  - **Atributo `overlay`**: Es un "Efecto Rápido". Se aplica solo a ese activo. Si el activo cambia, el overlay desaparece a menos que el nuevo activo también lo tenga.
- `<overlay type="dust" opacity="0.4" />`: Es una "Capa Global".
  - **Tag `<overlay />`**: Funciona de forma independiente. Puede mantenerse activo mientras cambian varios `<asset />` debajo de él. Ideal para mantener un estilo visual (ej: "vieja película") en toda la escena.

## ⚙️ Parámetros Avanzados
Todas las etiquetas aceptan parámetros opcionales:
- `volume`: Escala de 0.0 a 1.0 (ej: `0.5`).
- `duration`: Tiempo en segundos (ej: `2.5`).
- `type`: Nombre del archivo en la carpeta correspondiente.

### 🎥 Activos de Video (.mp4)
Si el `<asset />` es un video:
- **Loop Automático**: Si el video es más corto que el diálogo, Bill lo repetirá hasta cubrir el tiempo.
- **Audio de Fondo**: Bill silenciará el video automáticamente para que no compita con el narrador, a menos que se especifique lo contrario.
- **Limitación Alpha**: Los parámetros `zoom` y `move` (Ken Burns) se ignoran en videos; se muestran a pantalla completa.

## ✍️ Ejemplo de Guion Pro (Mezcla de Efectos)
```xml
<scene title="Catástrofe Inminente">
  <asset type="earth.png" zoom="1.1:1.5" overlay="glitch" />
  <ambient state="start" type="rumble" volume="0.3" />
  <voice name="es-ES-AlvaroNeural">
    [TENSO] El tiempo se agota <sfx type="heavy_hit" />... [/TENSO]
  </voice>
  <asset type="clock.png" zoom="1.0:1.2" move="VER:20:80" />
  Y recuerda... ¡el futuro es hoy!
</scene>
```

---
> [!TIP]
> **El Futuro es Hoy**: AVGL permite que el guion sea el director. Bill se encargará de interpretar cada etiqueta para sincronizar audio y video a la perfección.
