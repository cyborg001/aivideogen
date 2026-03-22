import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv(r"c:\Users\hp\aivideogen\agent_bridge\.env")

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def check_recent_emails():
    try:
        print(f"Conectando a {IMAP_SERVER} como {EMAIL_USER}...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Buscar los últimos 10 correos
        status, messages = mail.search(None, 'ALL')
        if status != "OK":
            print("No se pudo buscar correos.")
            return

        mail_ids = messages[0].split()
        last_ids = mail_ids[-10:] # Últimos 10

        print("\n--- ÚLTIMOS 10 CORREOS ---")
        for num in reversed(last_ids):
            status, data = mail.fetch(num, "(RFC822)")
            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
            
            from_ = msg.get("From")
            date_ = msg.get("Date")
            
            print(f"Fecha: {date_}")
            print(f"De: {from_}")
            print(f"Asunto: {subject}")
            
            if "Delivery Status Notification" in subject or "Mail Delivery Subsystem" in from_:
                print("⚠️ ¡DETECTADO REBOTE (BOUNCE)!")
                # Intentar leer el cuerpo para ver la razón
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                print(f"Snippet: {body[:500]}...")
            print("-" * 30)

        mail.logout()
    except Exception as e:
        print(f"Error en el diagnóstico: {e}")

if __name__ == "__main__":
    check_recent_emails()
