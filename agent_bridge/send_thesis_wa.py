import os
from twilio.rest import Client
from dotenv import load_dotenv
import sys

# Cargar variables de entorno
load_dotenv()

# Configuración de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
USER_WHATSAPP_NUMBER = os.getenv("AUTHORIZED_WHATSAPP")

def send_whatsapp_file_content(file_path):
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Twilio requiere el prefijo 'whatsapp:'
        from_wa = TWILIO_WHATSAPP_NUMBER if TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        to_wa = USER_WHATSAPP_NUMBER if USER_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{USER_WHATSAPP_NUMBER}"

        # El límite del Sandbox es de 1600 caracteres.
        summary = content[:1000] + "\n\n...(Contenido truncado por límite de caracteres)..."
        
        explanation = ("⚠️ Arquitecto, el archivo de la tesis excede el límite de caracteres de WhatsApp Sandbox (1600).\n\n"
                       "He guardado el archivo final en su sistema local. ¿Desea que se lo envíe ahora mismo por CORREO ELECTRÓNICO para preservar el formato y la integridad del documento? #email\n\n"
                       "Aquí tiene el inicio del documento:")

        # Enviar explicación
        client.messages.create(
            from_=from_wa,
            body=explanation,
            to=to_wa
        )

        # Enviar inicio de la tesis
        message = client.messages.create(
            from_=from_wa,
            body=summary,
            to=to_wa
        )
        
        print(f"Contenido enviado con éxito. SID: {message.sid}")
        
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")

if __name__ == "__main__":
    thesis_path = r"c:\Users\hp\aivideogen\tesis carlos\Tesis_Mw_ML_Final.md"
    send_whatsapp_file_content(thesis_path)
