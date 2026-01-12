# ⚙️ GUÍA DE CONFIGURACIÓN (.env)

El archivo `.env` controla el poder de tu aplicación. Aquí te explicamos cómo optimizarlo.

## 1. CONFIGURACIÓN BÁSICA (100% GRATIS)
Si no quieres pagar por APIs, usa lo siguiente:
- **TTS**: Por defecto usa `Edge TTS` (Microsoft), que es gratuito y de alta calidad.
- **Voz**: Cambia `EDGE_VOICE` por tu favorita (ej: `es-ES-AlvaroNeural`).
- **Velocidad**: Usa `EDGE_RATE` para acelerar o ralentizar la voz (ej: `+15%` para Reels rápidos). Por defecto está en `+15%`.

## 2. GEMINI AI (Generación de Guiones)
Para que la IA escriba los guiones por ti:
1. Obtén una API KEY en [Google AI Studio](https://aistudio.google.com/).
2. Ponla en `GEMINI_API_KEY`.
3. **Modelos**: El sistema usa `gemini-2.5-flash` por defecto (Ultra rápido). Puedes cambiarlo en `GEMINI_MODEL_NAME`.

## 3. ELEVENLABS (Voces Premium)
Para voces humanas reales:
1. Consigue tu API KEY en ElevenLabs.
2. Configura `ELEVENLABS_API_KEY`.
3. Selecciona el ID de la voz en la interfaz de la app.

## 4. OTRAS VARIABLES
- `PORT`: Por defecto 8888. Puedes cambiarlo si el puerto está ocupado.
- `MYMEMORY_EMAIL`: (Opcional) Para mejorar el límite de traducción de noticias.

---
⚠️ **IMPORTANTE**: Nunca compartas tu archivo `.env`. Contiene tus llaves privadas.
