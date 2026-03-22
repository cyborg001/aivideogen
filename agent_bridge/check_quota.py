import imaplib
import os
from dotenv import load_dotenv

load_dotenv(r"c:\Users\hp\aivideogen\agent_bridge\.env")

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def check_quota():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        # Obtener cuota
        quota = mail.getquotaroot("INBOX")
        print(f"Información de cuota: {quota}")
        
        # Ver si hay correos UNSEEN con [BILL-MISSION]
        mail.select("INBOX")
        status, messages = mail.search(None, '(UNSEEN SUBJECT "[BILL-MISSION]")')
        if status == "OK":
            unseen_count = len(messages[0].split())
            print(f"Correos no leídos con [BILL-MISSION]: {unseen_count}")
        
        mail.logout()
    except Exception as e:
        print(f"Error al verificar cuota: {e}")

if __name__ == "__main__":
    check_quota()
