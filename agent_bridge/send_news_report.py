import os
from twilio.rest import Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Twilio
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
USER_WHATSAPP_NUMBER = os.getenv("AUTHORIZED_WHATSAPP")

def send_news_report():
    report = """🚀 *REPORTE BILL: CUMBRE TECNOLÓGICA (MARZO 2026)* 🤖🔬

Arquitecto, aquí tienes lo más impactante de este mes:

*1. Inteligencia Artificial (IA)*
- *GPT-5.4:* OpenAI supera benchmarks humanos en razonamiento y codificación. Ventana de contexto de 1M de tokens.
- *DeepSeek V4:* Lanzamiento con 1 trillón de parámetros y pesos abiertos.
- *AMI Labs:* Yann LeCun deja Meta y funda AMI con $1B para crear "Modelos de Mundo" para robótica.
- *IA Agéntica:* La tendencia del mes. Sistemas autónomos que ejecutan flujos completos.

*2. Ciencia*
- *Internet Cuántico:* Primera teletransportación exitosa entre puntos cuánticos distintos.
- *Química Estelar:* Tres nuevos descubrimientos explican el origen del oro en el cosmos.
- *Genética:* Archivo de ADN de 400 millones de años identificado para mejorar cultivos.

*3. Tecnología y Espacio*
- *Baterías de Estado Sólido:* China reduce costos y acelera patentes.
- *Estaciones Espaciales Comerciales:* El espacio se convierte en laboratorio privado orbital.

Bill siempre alerta. ¿Deseas más detalles sobre algún punto? 🫡"""

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        from_wa = TWILIO_WHATSAPP_NUMBER if TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
        to_wa = USER_WHATSAPP_NUMBER if USER_WHATSAPP_NUMBER.startswith("whatsapp:") else f"whatsapp:{USER_WHATSAPP_NUMBER}"

        message = client.messages.create(
            from_=from_wa,
            body=report,
            to=to_wa
        )
        print(f"Reporte de noticias enviado. SID: {message.sid}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_news_report()
