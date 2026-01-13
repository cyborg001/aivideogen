# 📜 MANUAL: AVGL (AI Video Generation Language) v3.0

Bienvenido al lenguaje de edición **AVGL**. Este sistema sustituye el formato de columnas por un lenguaje de marcado estructurado que otorga control total sobre cada milisegundo del video.

## 🏗️ Estructura Jerárquica (v3.0 Plus Plus)
AVGL utiliza ahora una estructura de "Capas de Cebolla" para un control organizacional máximo:

1.  **Raíz `<avgl title="..." voice="..." speed="..." style="...">`**: Contenedor maestro.
    - **Efecto**: Define la configuración global. Los atributos de voz se heredan por defecto a todo el video.
2.  **Partes `<bloque title="..." music="..." voice="..." speed="..." style="...">`**: Agrupadores narrativos.
    - **Efecto**: Sobrescribe la configuración global para todas las escenas internas.
3.  **Capítulos `<scene title="...">`**: Unidades de acción e imagen.
4.  **Voz `<voice name="..." speed="..." style="...">`**: Contenedor obligatorio de la narración.
    - **Efecto**: Todo el texto DEBE estar dentro de esta etiqueta para que Bill lo procese y sincronice correctamente.

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
- `<music state="change" type="nombre_pista" volume="0.2" />`: Cambia la pista de fondo de forma dinámica en medio de una escena.
- `<music state="stop" />`: Detiene la música actual.
- `<camera zoom="1.0:1.3" move="HOR:0:100" />`: Realiza un re-encuadre (Ken Burns) sin cambiar el activo visual.

### 🎙️ Capa de Abstracción de Voz
Bill actúa como traductor universal para que el guion sea compatible con múltiples motores (Edge TTS, ElevenLabs).
- `<voice name="es-MX-JorgeNeural"> ... </voice>`: Cambia el narrador actual.
- **Etiquetas de Emoción (Abstractas)**:
  - `[TENSO] texto [/TENSO]`: Tono bajo y velocidad lenta. Ideal para advertencias o drama.
  - `[EPICO] texto [/EPICO]`: Aumenta el volumen, velocidad e intensidad.
  - `[SUSPENSO] texto [/SUSPENSO]`: Ritmo muy lento con tono profundo.
  - `[GRITANDO] texto [/GRITANDO]`: Volumen al máximo y tono agudo.
  - `[SUSURRO] texto [/SUSURRO]`: Volumen mínimo y tono muy bajo para momentos secretos.

### ⏱️ Control de Tiempo
- `<pause duration="1.5" />`: Introduce un silencio dramático. Durante la pausa, los efectos visuales y el ambiente continúan.

### 🎬 Disparadores Visuales e In-Line
- `<asset type="imagen.png" zoom="1.0:1.3" move="HOR:0:100" overlay="grain" />`: Cambia el activo y aplica efectos.
  - **Atributo `overlay`**: Es un "Efecto Rápido". Se aplica solo a ese activo.
- `<overlay type="dust" opacity="0.4" />`: Es una "Capa Global" (ej: `dust`, `grain`, `light_leaks`).

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

## 🎬 Ejemplo de "Programación Visual"
```xml
<avgl title="Demo Rápida">
  <scene title="La Revelación">
    <asset type="eye_robotic_closed.png" zoom="1.1:1.3" />
    <voice name="es-ES-AlvaroNeural">
      Él lo sabía... <pause duration="0.8" />
      <sfx type="Webdriver_Torso" />
      <asset type="eye_robotic_open.png" zoom="1.0:1.5" overlay="grain" />
      [SUSURRO] La fecha es inevitable. [/SUSURRO]
    </voice>
  </scene>
</avgl>
```

## ✍️ Ejemplo de Guion Pro (Mezcla de Efectos)
```xml
<avgl title="Script Maestro">
  <bloque title="El Inicio" music="Space Station Experience - Unicorn Heads">
    <scene title="Catástrofe Inminente">
      <asset type="earth_from_space_dark.png" zoom="1.1:1.5" overlay="dust" />
      <ambient state="start" type="laboratory_hum" volume="0.3" />
      <voice name="es-ES-AlvaroNeural">
        [TENSO] El tiempo se agota <sfx type="Debris_Hits" />... [/TENSO]
      </voice>
      <asset type="doomsday_countdown_clock.png" zoom="1.0:1.2" move="VER:20:80" />
      <voice name="es-ES-AlvaroNeural">
        Y recuerda... [GRITANDO]¡el futuro es hoy![/GRITANDO]
      </voice>
    </scene>
  </bloque>
</avgl>
```

---
> [!TIP]
> **El Futuro es Hoy**: AVGL permite que el guion sea el director. Bill se encargará de interpretar cada etiqueta para sincronizar audio y video a la perfección.
