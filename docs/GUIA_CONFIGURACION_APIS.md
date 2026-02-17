# 🛠️ Guía de Configuración de APIs y Entorno

Para que **AIVideogen** funcione a plena potencia, necesitas configurar dos servicios clave de Google: **Gemini (IA)** y **YouTube (Subida Automática)**. Sigue estos pasos.

---

## 1. 🧠 Google Gemini API (El "Cerebro")

Esta API permite al sistema generar guiones, investigar temas y analizar datos.

1.  Ve a [Google AI Studio](https://makersuite.google.com/app/apikey).
2.  Inicia sesión con tu cuenta de Google.
3.  Haz clic en **"Create API key"**.
4.  Copia la clave generada (empieza por `AIza...`).
5.  Abre el archivo `.env` en la raíz del proyecto (si no existe, renombra `.env.example` a `.env`).
6.  Pega tu clave:
    ```ini
    GEMINI_API_KEY=AIzaSyD...TUS_CARACTERES
    ```

---

## 2. 📺 YouTube Data API (La "Voz" al Mundo)

Esta configuración permite que el sistema suba videos automáticamente a tu canal.

### Paso A: Crear Proyecto en Google Cloud
1.  Ve a [Google Cloud Console](https://console.cloud.google.com/).
2.  Crea un **Nuevo Proyecto** (llámalo `aivideogen-uploader`).
3.  En el menú lateral, ve a **APIs y servicios > Biblioteca**.
4.  Busca **"YouTube Data API v3"** y actívala.

### Paso B: Pantalla de Consentimiento OAuth
1.  Ve a **APIs y servicios > Pantalla de consentimiento de OAuth**.
2.  Elige **Externo** (para pruebas personales) y dale a Crear.
3.  Rellena los campos obligatorios (nombre de app, email).
4.  En **Usuarios de prueba**, añade tu propio correo de Gmail (el del canal de YouTube).

### Paso C: Credenciales
1.  Ve a **APIs y servicios > Credenciales**.
2.  Haz clic en **Crear Credenciales > ID de cliente de OAuth**.
3.  Tipo de aplicación: **Aplicación de escritorio**.
4.  Dale un nombre y haz clic en **Crear**.
5.  **IMPORTANTE**: Descarga el archivo JSON (botón de descarga a la derecha).
6.  Renombra ese archivo a `client_secrets.json`.
7.  Mueve el archivo a la raíz de la carpeta `aivideogen/`.

---

## 3. 🗣️ ElevenLabs (Opcional - Voces Premium)

Si quieres voces ultra-realistas (más allá de las gratuitas de EdgeTTS):

1.  Regístrate en [ElevenLabs.io](https://elevenlabs.io/).
2.  Ve a tu perfil > **API Key**.
3.  Copia la clave y pégala en `.env`:
    ```ini
    ELEVENLABS_API_KEY=tu_clave_aqui
    ```

---

## 🎬 Showcase: AIVideogen en Acción

¿Qué puedes lograr con esta configuración? Mira este ejemplo generado 100% automáticamente:

[![Video Demo](https://img.youtube.com/vi/TU_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=TU_VIDEO_ID)

*(Reemplaza este enlace con tu mejor video generado)*

---

**Nota**: Nunca compartas tu `.env` ni tu `client_secrets.json`. Contienen acceso directo a tu cuenta.
