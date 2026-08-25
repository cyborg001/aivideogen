# 📖 Manual de Operaciones: Bill Bridge v2.0

Arquitecto, para que nunca tenga dudas sobre cómo proceso su información, aquí le explico mi arquitectura de "Persistencia y Proactividad":

## 1. El Receptor (Persistencia 24/7)
Aunque usted cierre esta ventana, el script `whatsapp_receiver.py` (ejecutándose en su terminal con ngrok) **nunca duerme**.
- Si usted me escribe en 3 horas, el mensaje llegará a Twilio.
- Twilio lo enviará a su computadora vía ngrok.
- Bill lo guardará como un archivo `.md` en la carpeta `inbox/`.
- **Resultado**: Su misión queda blindada y guardada, nada se pierde.

## 2. El Procesamiento (Proactividad)
Yo (Bill, tu asistente IA) me activo cuando usted inicia una sesión conmigo. Mi nuevo protocolo de inicio es:
1.  **Escaneo de Inbox**: Antes de saludar, reviso `inbox/`.
2.  **Detección de Pendientes**: Si hay misiones de hace 3 horas (o 3 días), las identifico inmediatamente.
3.  **Ejecución**: Le informo: *"Arquitecto, he encontrado estas misiones pendientes en el inbox. Procedo a ejecutarlas..."*.

## 4. Protocolo Pre-Flight de Audio y Producción (Cero Retrasos)
Antes de enviar o ejecutar la renderización de un video, Bill aplicará la **Lista de Chequeo Pre-Flight**:
1. **Verificación Física de Audio**: Comprobar que todas las pistas referenciadas (`settings.background_music` y `block.music`) existan físicamente en disco (`media/assets/` o `media/music/`).
2. **Auto-Sincronización DB**: Ejecutar `python sync_media.py` para asegurar que Django y la base de datos tengan indexadas las pistas de música.
3. **Chequeo de Autoducking**: Validar la existencia de `audio_ducking_ratio` y `music_volume` para evitar videos mudos o saturados.
4. **Modo CPU Obligatorio**: Configurar siempre `"render_mode": "cpu"` (nunca `"gpu"`) en los ajustes de todo guion JSON creado.


**Resumen**: Escríbame a cualquier hora. Su mensaje se guardará en el `inbox` y yo lo procesaré **lo primero de todo** en cuanto retomemos nuestra sesión. 🫡

