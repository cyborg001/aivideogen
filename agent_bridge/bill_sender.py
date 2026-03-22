import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
AUTHORIZED_SENDER = os.getenv("AUTHORIZED_SENDER")

from whatsapp_sender import send_whatsapp_message

def send_detailed_report(channel="email"):
    """
    Envía el reporte detallado al Arquitecto por el canal especificado.
    """
    if not AUTHORIZED_SENDER and channel == "email":
        print("Error: No hay un remitente autorizado configurado en .env")
        return

    # Leer resumen de PRISMA para el cuerpo
    prisma_path = r"C:\Users\hp\.gemini\antigravity\brain\e6ef47a4-bf01-449b-b182-3f3bad29f855\implementation_plan.md"
    if not os.path.exists(prisma_path):
        prisma_path = r"C:\Users\hp\aivideogen\tesis carlos\Tesis_Mw_ML_Editable_Draft.md"
        
    try:
        with open(prisma_path, "r", encoding="utf-8") as f:
            prisma_summary = f.read()
    except Exception:
        prisma_summary = "Resumen no disponible en este momento."

    body = f"""Hola Arquitecto,
Tal como solicitaste, aquí tienes los detalles:

{prisma_summary}

Atentamente,
Bill - Tu Asistente Técnico Proactivo
"""

    if channel == "whatsapp":
        print("Enviando reporte vía WhatsApp...")
        return send_whatsapp_message(body[:1500]) # WhatsApp tiene límites de caracteres
    else:
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = AUTHORIZED_SENDER
            msg['Subject'] = "[BILL-UPDATE] Detalles Tesis Mw-ML"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            server.quit()
            print(f"Reporte enviado con éxito vía Email a {AUTHORIZED_SENDER}")
            return True
        except Exception as e:
            print(f"Error al enviar el reporte por Email: {e}")
            return False

if __name__ == "__main__":
    # Lógica de detección simple si se corre manualmente
    import sys
    canal = "whatsapp" if len(sys.argv) > 1 and sys.argv[1] == "--whatsapp" else "email"
    send_detailed_report(channel=canal)
