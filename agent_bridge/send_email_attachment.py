import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
AUTHORIZED_SENDER = os.getenv("AUTHORIZED_SENDER")

def send_file_by_email(file_path):
    if not os.path.exists(file_path):
        print(f"Error: El archivo {file_path} no existe.")
        return

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = AUTHORIZED_SENDER
        msg['Subject'] = f"[BILL-ENTREGA] Archivo de Tesis: {os.path.basename(file_path)}"
        
        body = "Hola Arquitecto,\n\nTal como solicitó por WhatsApp, aquí le envío el archivo de la tesis con todos los ajustes de paridad y rigor PRISMA aplicados.\n\nAtentamente,\nBill"
        msg.attach(MIMEText(body, 'plain'))

        # Adjuntar archivo
        filename = os.path.basename(file_path)
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        msg.attach(part)
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        
        print(f"Archivo enviado con éxito a {AUTHORIZED_SENDER}")
        return True
    except Exception as e:
        print(f"Error al enviar el email: {e}")
        return False

if __name__ == "__main__":
    thesis_path = r"c:\Users\hp\aivideogen\tesis carlos\Tesis_Mw_ML_Final.md"
    send_file_by_email(thesis_path)
