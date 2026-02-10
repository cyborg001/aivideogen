# ⚙️ Modos de Configuración: Gratis vs Pro

aiVideoGen es una herramienta flexible que puede funcionar de forma totalmente gratuita o escalada con APIs profesionales para obtener resultados de nivel cine.

---

## 🟢 Modo GRATIS (Recomendado para empezar)
Este modo no requiere tarjetas de crédito ni suscripciones. Utiliza servicios gratuitos de alta calidad.

### 1. Voz (Edge TTS)
Utiliza el motor de Microsoft Edge para generar voces naturales sin costo.
*   **Configuración**: En el archivo `.env`, asegúrate de tener:
    ```bash
    EDGE_VOICE=es-DO-EmilioNeural
    EDGE_RATE=+15%
    ```
*   **Ventaja**: Es ilimitado y gratuito. No requiere API Key.

### 2. Guiones (Manual / Guía de Prompts)
Puedes escribir tus propios guiones siguiendo el estándar AVGL o usar nuestra [Guía de Prompts IA](./GUIA_PROMPTS_IA.md) para generar el JSON en ChatGPT o Gemini (versión gratuita).

---

## 🔵 Modo PRO (Máxima Potencia)
Si buscas automatización total y voces humanas indistinguibles, activa estos módulos.

### 1. Generación Automática (Gemini AI)
Permite que la app cree el guion, asigne efectos visuales y elija assets por ti. Requiere una API Key de Google.
*   **Obtención**: Gratis (con límites generosos) en [Google AI Studio](https://aistudio.google.com/).
*   **Configuración**:
    ```bash
    GEMINI_API_KEY=tu_key_aqui
    GEMINI_MODEL_NAME=gemini-2.5-flash
    ```

### 2. Voces Ultra-Realistas (ElevenLabs)
La mejor tecnología de voz del mundo integrada en aiVideoGen.
*   **Configuración**:
    ```bash
    ELEVENLABS_API_KEY=tu_key_aqui
    ```

---

## 📁 Archivos de Configuración
Antes de arrancar, debes preparar tus archivos de base:
1. **`.env`**: Copia `.env.example` y renómbralo a `.env`. Ajusta tus preferencias aquí.
2. **`client_secrets.json`**: (Opcional) Si quieres subir automáticamente a YouTube, copia `client_secrets.json.example` y rellénalo con tus credenciales de Google Cloud Console.

---
**Nota:** aiVideoGen es un software local. Tus APIs y datos nunca salen de tu máquina hacia nuestros servidores.
