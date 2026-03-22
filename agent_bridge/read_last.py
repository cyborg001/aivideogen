import imaplib
import email
import os
from dotenv import load_dotenv

load_dotenv(r"c:\Users\hp\aivideogen\agent_bridge\.env")

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def read_last_email_body():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, 'ALL')
        mail_ids = messages[0].split()
        last_id = mail_ids[-1]

        status, data = mail.fetch(last_id, "(RFC822)")
        msg = email.message_from_bytes(data[0][1])
        
        print(f"Asunto: {msg.get('Subject')}")
        
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        
        print("\n--- CUERPO ---")
        print(body)

        mail.logout()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    read_last_email_body()
