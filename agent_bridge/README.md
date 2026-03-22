# Bill Bridge v1.0 - Instrucciones de Configuración 🚀

Este sistema permite que Bill reciba instrucciones vía email. Sigue estos pasos para activarlo:

## 1. Configuración de Gmail (Recomendado)
Para que el script pueda leer tus correos, necesitas una **Contraseña de Aplicación**:
1. Entra en tu [Cuenta de Google](https://myaccount.google.com/).
2. Ve a **Seguridad**.
3. En "Acceso a Google", busca **Contraseñas de aplicaciones** (debes tener la Verificación en 2 pasos activa).
4. Selecciona App: `Otra (nombre personalizado)` y escribe `Bill Bridge`.
5. Copia el código de 16 caracteres generado.

## 2. Configurar el archivo .env
Edita el archivo `agent_bridge/.env` con tus datos:
```bash
IMAP_SERVER=imap.gmail.com
EMAIL_USER=tu_correo@gmail.com
EMAIL_PASS=tu_codigo_de_16_caracteres
AUTHORIZED_SENDER=tu_correo_personal@dominio.com
```

## 3. Ejecución
Para que Bill esté siempre atento, el script debe estar corriendo. Puedes ejecutarlo con:
```bash
python agent_bridge/bill_receiver.py
```

## 4. Envío de Misiones
Para enviar una instrucción a Bill:
- **Asunto**: Debe empezar con `[BILL-MISSION]`. Ejemplo: `[BILL-MISSION] Analiza la tendencia de IA de hoy`.
- **Cuerpo**: Escribe tus instrucciones con detalle. Bill las encontrará en la carpeta `inbox/` al iniciar su próxima tarea.
