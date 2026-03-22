import os
from twilio.rest import Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886") # Sandbox number por defecto
USER_WHATSAPP_NUMBER = os.getenv("AUTHORIZED_WHATSAPP")

def send_whatsapp_message(body):
    """
    Envía un mensaje de WhatsApp al Arquitecto.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, USER_WHATSAPP_NUMBER]):
        print("Error: Credenciales de Twilio o número de destino no configurados en .env")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Twilio requiere el prefijo 'whatsapp:' para este canal
        from_wa = TWILIO_WHATSAPP_NUMBER if TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        to_wa = USER_WHATSAPP_NUMBER if USER_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{USER_WHATSAPP_NUMBER}"

        message = client.messages.create(
            from_=from_wa,
            body=body,
            to=to_wa
        )
        
        print(f"Mensaje enviado con éxito. SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Error al enviar mensaje de WhatsApp: {e}")
        return False

if __name__ == "__main__":
    # Prueba rápida
    test_body = "Hola Arquitecto, Bill ha iniciado la integración de WhatsApp con éxito. 🚀"
    send_whatsapp_message(test_body)
