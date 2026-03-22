import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")  # Usar Contraseña de Aplicación
AUTHORIZED_SENDER = os.getenv("AUTHORIZED_SENDER")
INBOX_DIR = "inbox"

import logging

# Configuración de logs
LOG_FILE = os.path.join(os.path.dirname(__file__), "agent_bridge.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

if not os.path.exists(INBOX_DIR):
    os.makedirs(INBOX_DIR)

from whatsapp_sender import send_whatsapp_message

def send_reply(to_email, original_subject, channel="email"):
    try:
        body = f"""Hola Arquitecto,

He recibido tu misión con éxito: "{original_subject}".

Ya he guardado las instrucciones en mi sistema de prioridad y estoy trabajando en ello ahora mismo. Te avisaré por esta vía o en nuestra próxima sesión en cuanto tenga resultados.

Atentamente,
Bill - Tu Asistente Técnico Proactivo"""

        if channel == "whatsapp":
            send_whatsapp_message(body)
            print(f"Respuesta de WhatsApp enviada.")
        else:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = to_email
            msg['Subject'] = f"Re: {original_subject} - [BILL-MISSION RECIBIDA]"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
            server.quit()
            print(f"Respuesta de Email enviada a {to_email}")
            
    except Exception as e:
        print(f"Error al enviar respuesta: {e}")

def check_email():
    try:
        # Conectar al servidor
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Buscar correos no leídos con el tag [BILL-MISSION]
        status, messages = mail.search(None, '(UNSEEN SUBJECT "[BILL-MISSION]")')
        
        if status != "OK":
            return

        for num in messages[0].split():
            # Obtener el mensaje completo
            status, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decodificar el remitente
            from_ = msg.get("From")
            sender_email = email.utils.parseaddr(from_)[1]
            if AUTHORIZED_SENDER and AUTHORIZED_SENDER not in from_:
                print(f"Ignorando correo de remitente no autorizado: {from_}")
                continue

            # Decodificar el asunto
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")

            print(f"Procesando misión: {subject}")

            # Extraer el cuerpo del mensaje
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = msg.get_payload(decode=True).decode()

            # Determinar canal y ruteo
            channel = "email"
            if "#whatsapp" in body.lower():
                channel = "whatsapp"
            elif "#email" in body.lower():
                channel = "email"

            # Guardar en archivo Markdown
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mission_{timestamp}.md"
            filepath = os.path.join(INBOX_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Misión: {subject}\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Remitente: {from_}\n")
                f.write(f"Canal Origen: Email\n")
                f.write(f"Canal Respuesta: {channel}\n\n")
                f.write("## Instrucciones Originales\n\n")
                f.write(body)

            print(f"Misión guardada en: {filepath} (Respuesta por: {channel})")
            
            # Enviar confirmación automática
            send_reply(sender_email, subject, channel=channel)

        mail.logout()
    except Exception as e:
        print(f"Error en Bill Bridge: {e}")

if __name__ == "__main__":
    print("Bill Bridge (Receptor de Misiones) Iniciado...")
    while True:
        check_email()
        time.sleep(30)  # Revisar cada 30 segundos
