# 📺 GUÍA DE CONFIGURACIÓN DE YOUTUBE

Esta guía te ayudará a configurar la integración con YouTube para subir videos automáticamente desde la aplicación.

---

## 📋 REQUISITOS PREVIOS

- Una cuenta de Google
- Acceso a [Google Cloud Console](https://console.cloud.google.com/)
- La aplicación corriendo en `http://127.0.0.1:8888`

---

## 🔧 PASO 1: CREAR PROYECTO EN GOOGLE CLOUD

1. Ve a https://console.cloud.google.com/
2. Haz clic en el **selector de proyecto** (parte superior)
3. Clic en **"Nuevo proyecto"**
4. Nombre del proyecto: `AI Video Generator` (o el que prefieras)
5. Haz clic en **"Crear"**
6. Espera unos segundos a que se cree el proyecto
7. Selecciona el proyecto recién creado

---

## 🎯 PASO 2: HABILITAR YOUTUBE DATA API v3

1. En el menú lateral, ve a **"APIs y servicios"** > **"Biblioteca"**
2. Busca: `YouTube Data API v3`
3. Haz clic en el resultado
4. Haz clic en **"Habilitar"**
5. Espera a que se active (puede tardar 1-2 minutos)

---

## 🔑 PASO 3: CREAR CREDENCIALES OAUTH 2.0

### 3.1 Configurar Pantalla de Consentimiento

1. Ve a **"APIs y servicios"** > **"Pantalla de consentimiento de OAuth"**
2. Selecciona **"Externo"** (para uso personal)
3. Haz clic en **"Crear"**

4. Completa el formulario:
   - **Nombre de la app**: `aiVideoGen`
   - **Correo de asistencia**: Tu email
   - **Logo**: (opcional)
   - **Dominio de la app**: (dejar vacío)
   - **Correo del desarrollador**: Tu email

5. Haz clic en **"Guardar y continuar"**

6. En **"Permisos"**: Haz clic en **"Agregar o quitar permisos"**
   - Busca: `youtube.upload`
   - Selecciona: **YouTube Data API v3 - .../auth/youtube.upload**
   - Haz clic en **"Actualizar"**
   - Haz clic en **"Guardar y continuar"**

7. En **"Usuarios de prueba"**: Agrega tu email de YouTube
   - Haz clic en **"+ ADD USERS"**
   - Escribe tu email
   - Haz clic en **"Guardar"**

8. Haz clic en **"Guardar y continuar"** hasta terminar

### 3.2 Crear ID de Cliente OAuth

1. Ve a **"APIs y servicios"** > **"Credenciales"**
2. Haz clic en **"+ CREAR CREDENCIALES"**
3. Selecciona **"ID de cliente de OAuth 2.0"**

4. Configuración:
   - **Tipo de aplicación**: `Aplicación de escritorio`
   - **Nombre**: `AI Video Generator Desktop`

5. Haz clic en **"Crear"**

6. Aparecerá un mensaje "Cliente de OAuth creado"
   - Haz clic en **"DESCARGAR JSON"**
   - **IMPORTANTE**: Guarda este archivo, lo necesitarás en el siguiente paso

---

## 📁 PASO 4: CONFIGURAR client_secrets.json

1. Renombra el archivo descargado a: `client_secrets.json`
2. Copia el archivo a la carpeta raíz de la aplicación:
   ```
   web_app2/web_app/client_secrets.json
   ```

El archivo debe quedar en la misma carpeta donde está `run_app.py`

---

## 🌐 PASO 5: CONFIGURAR URIs DE REDIRECCIÓN

**IMPORTANTE**: Google Cloud Console necesita saber a dónde enviar la respuesta de autenticación.

1. Ve a **"APIs y servicios"** > **"Credenciales"**
2. Haz clic en tu **ID de cliente OAuth 2.0** (el que acabas de crear)
3. En **"URIs de redirección autorizados"**, haz clic en **"+ AGREGAR URI"**
4. Agrega **EXACTAMENTE** esta URI:
   ```
   http://127.0.0.1:8888/youtube/callback/
   ```
   ⚠️ **IMPORTANTE**:
   - Debe ser `127.0.0.1` (no `localhost`)
   - Puerto `8888` (el puerto de la aplicación)
   - Incluir la `/` final en `/callback/`
   - Usar `http://` (no `https://`)

5. Haz clic en **"Guardar"**
6. **Espera 1-2 minutos** para que Google actualice la configuración

---

## 🏷️ **PERSONALIZAR HASHTAGS (OPCIONAL)**

Puedes personalizar los hashtags fijos que aparecen en todos tus videos.

1. Abre el archivo `.env` en la carpeta raíz
2. Busca o agrega la línea:
   ```bash
   YOUTUBE_FIXED_HASHTAGS=#TuMarca #tecnologia #innovacion #futuro
   ```
3. Cambia los hashtags por los de tu marca
4. **Importante**: 
   - Separa los hashtags con espacios
   - Incluye el símbolo `#` en cada uno
   - Máximo 9-12 hashtags recomendados

**Ejemplo**:
```bash
YOUTUBE_FIXED_HASHTAGS=#MiCanal #IA #tech #ciencia #futuro #innovacion
```

**Comportamiento**:
- Estos hashtags aparecerán **después** de los hashtags específicos del guion
- Si no defines esta variable, se usarán hashtags por defecto

---

## ✅ PASO 6: PROBAR LA INTEGRACIÓN

1. **Inicia la aplicación**:
   - Ejecuta `AI_Video_Generator_v2.20.0.exe` o `python run_app.py`

2. **Genera un video** (si no tienes uno ya)

3. **Ve a la página del video**

4. **Haz clic en "Subir a YouTube"**
   - Se abrirá una nueva pestaña con Google
   - Inicia sesión con tu cuenta de YouTube
   - Acepta los permisos solicitados
   - La ventana se cerrará automáticamente

5. **¡Listo!** El video se subirá a YouTube

---

## 🔄 REUTILIZACIÓN

Solo necesitas hacer esta configuración **UNA VEZ**. Después de autorizar:
- El token se guarda en la base de datos
- Los siguientes videos se subirán automáticamente
- No necesitas volver a autorizar

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "redirect_uri_mismatch"
**Causa**: La URI de redirección no coincide exactamente.

**Solución**:
1. Verifica que en Google Cloud Console tengas: `http://127.0.0.1:8888/youtube/callback/`
2. Verifica que la aplicación corra en puerto 8888
3. Espera 1-2 minutos después de cambiar la URI

### Error: "invalid_grant: Token has been expired or revoked"
**Causa**: El token guardado expiró.

**Solución**:
1. Haz clic en "Subir a YouTube" nuevamente
2. Vuelve a autorizar la aplicación
3. El token se renovará automáticamente

### Error: "FileNotFoundError: client_secrets.json"
**Causa**: El archivo no está en la ubicación correcta.

**Solución**:
1. Verifica que `client_secrets.json` esté en: `web_app2/web_app/`
2. Debe estar en la misma carpeta que `run_app.py`

### Error: "ERR_CONNECTION_REFUSED" después de autorizar
**Causa**: La aplicación no está corriendo o el puerto es incorrecto.

**Solución**:
1. Asegúrate de que la aplicación esté corriendo
2. Verifica que corra en puerto 8888 (no 8000 u otro)
3. Reinicia la aplicación si es necesario

---

## 📧 SOPORTE

Si tienes problemas con la configuración:
- Email: carlosaipro6@gmail.com
- Incluye capturas de pantalla del error
- Especifica en qué paso tuviste el problema

---

**Última actualización**: 2026-01-07
