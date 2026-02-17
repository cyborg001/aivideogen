# 🎬 AIVideogen - Automated AI Video Engine (AVGL v4.0)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Beta-orange?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**AIVideogen** es un motor de generación de video automatizado impulsado por Inteligencia Artificial. Utiliza scripts en formato **AVGL (Audio-Visual Generation Language)** para crear contenido audiovisual complejo, con narración neuronal (EdgeTTS/ElevenLabs), subtítulos dinámicos estilo karaoke y efectos visuales cinematográficos.

## ✨ Características Principales

- **🗣️ Narración Neuronal**: Soporta voces ultra-realistas de **ElevenLabs** y **EdgeTTS** (gratuito) con emociones (`[TENSO]`, `[EPICO]`, `[SUSURRO]`).
- **🎵 Sincronización Karaoke Precisa**: Sistema de *Auto-Calibración* y *Global Offset* (-80ms) para garantizar que los subtítulos `[DYN]` vayan al ritmo exacto de la voz.
- **📜 Scripting AVGL v4.0**: Un lenguaje JSON o Pipe-Separated (`|`) diseñado para controlar cada aspecto del video:
    - `ZOOM:1.5:1.0`, `MOVE:HOR:50:50`, `SHAKE:5`, `ROTATE:15`.
    - Grupos de escenas para mantener el "Master Shot".
- **⚡ Renderizado Híbrido**: Utiliza **FFmpeg** puro para velocidad y **MoviePy** para composición compleja.
- **🧠 Asistente IA Integrado**: Generación automática de guiones e investigación de temas.

## 💡 Casos de Uso Ideales

¿Para qué sirve **AIVideogen**? Es perfecto para creadores que quieren escalar su producción:

- **🕵️ Faceless Channels**: Crea videos de curiosidades, noticias, tops o misterio sin grabar nada (automatización 100%).
- **📚 Storytelling & Historia**: Narra eventos históricos, creepypastas o cuentos con música inmersiva, efectos de sonido y voces con emoción (`[TENSO]`, `[SUSURRO]`).
- **🎙️ Visual Podcasts**: Convierte tu guion de podcast en un video dinámico con subtítulos tipo karaoke para retener la atención.
- **📢 Marketing de Contenidos**: Genera videos promocionales rápidos para TikTok, Reels o Shorts.
- **🏫 Educación**: Explica conceptos complejos con una voz clara y diagramas visuales perfectamente sincronizados.

## 🚀 Instalación Rápida

1.  **Clonar el repositorio**:
    ```bash
    git clone https://github.com/tu-usuario/aivideogen.git
    cd aivideogen
    ```

2.  **Crear entorno virtual (Recomendado)**:
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Instalar dependencias**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar Variables de Entorno**:
    Crea un archivo `.env` en la raíz (usa `.env.example` como guía):
    ```ini
    # .env
    GEMINI_API_KEY=tu_api_key_de_google
    ELEVENLABS_API_KEY=tu_api_key_de_elevenlabs (Opcional)
    EDGE_TTS_RATE=+0%
    ```

    👉 **[Ver Guía Detallada de Configuración de APIs](docs/GUIA_CONFIGURACION_APIS.md)** (Google AI Studio, YouTube OAuth, ElevenLabs)

## 🎬 Showcase / Demo

Mira lo que **AIVideogen** puede crear de forma totalmente autónoma:

[![AIVideogen Demo](https://img.youtube.com/vi/-W2CiB3zAoU/0.jpg)](https://www.youtube.com/watch?v=-W2CiB3zAoU)

*(Ejemplo de video generado con AIVideogen: Narración, imágenes y subtítulos DYN)*

## 🎮 Uso Básico

> 🎓 **¿Nuevo creando videos?**  
> Mira nuestro **[Tutorial Paso a Paso: Tu Primer Guion](docs/TUTORIAL_CREACION_GUIONES.md)** para aprender a programar `.json` desde cero.

Para generar un video desde un guion JSON:

```bash
python run_engine.py --input "guiones/mi_guion.json" --output "render/final.mp4"
```

O usa el asistente interactivo:

```bash
python main.py
```

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si tienes una idea para mejorar el motor de renderizado, optimizar la sincronización de audio o añadir nuevas voces, por favor:

1.  Haz un Fork del proyecto.
2.  Crea una rama (`git checkout -b feature/AmazingFeature`).
3.  Haz Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`).
4.  Haz Push a la rama (`git push origin feature/AmazingFeature`).
5.  Abre un Pull Request.

Consulta `CONTRIBUTING.md` para más detalles.

## 💰 Apoya el Proyecto

Este proyecto es el resultado de cientos de horas de ingeniería inversa, pruebas de sincronización y pasión por la IA. Si te ha sido útil o quieres acelerar el desarrollo de nuevas funciones (como clonación de voz local o avatares 3D), considera hacer una donación:

- **☕ Buy me a Coffee**: [Enlace a tu Ko-fi/Patreon]
- **💖 GitHub Sponsors**: [Enlace a GitHub Sponsors]
- **💳 PayPal**: cgrs27@gmail.com

Tu apoyo mantiene los servidores de prueba encendidos y el café fluyendo. ¡Gracias!

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo `LICENSE` para más detalles.
