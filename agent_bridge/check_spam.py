import imaplib
import os
from dotenv import load_dotenv

load_dotenv(r"c:\Users\hp\aivideogen\agent_bridge\.env")

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def find_spam_and_unseen():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        
        # Listar carpetas para encontrar SPAM
        status, folders = mail.list()
        print("Carpetas encontradas:")
        for f in folders:
            print(f)
            
        # Buscar en Spam si existe
        spam_folder = '[Gmail]/Spam' # Común en Gmail
        status, _ = mail.select(spam_folder)
        if status == "OK":
            status, messages = mail.search(None, 'ALL')
            print(f"Mensajes en SPAM: {len(messages[0].split())}")
        
        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_spam_and_unseen()
