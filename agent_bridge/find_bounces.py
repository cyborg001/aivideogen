import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv(r"c:\Users\hp\aivideogen\agent_bridge\.env")

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def find_bounces():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Buscar correos con palabras clave de rebote
        keywords = ['failure', 'returned', 'undelivered', 'rebote', 'delivery']
        found = False
        
        for kw in keywords:
            status, messages = mail.search(None, f'SUBJECT "{kw}"')
            if status == "OK" and messages[0]:
                for num in messages[0].split():
                    status, data = mail.fetch(num, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    from_ = msg.get("From")
                    print(f"BOMBA DE REBOTE DETECTADA: {subject} (De: {from_})")
                    found = True
        
        if not found:
            print("No se encontraron rebotes obvios mediante búsqueda de palabras clave.")

        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_bounces()
