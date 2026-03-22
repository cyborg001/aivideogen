import imaplib
import os
from dotenv import load_dotenv

# Forzar carga de .env desde la ruta absoluta
load_dotenv(r"c:\Users\hp\aivideogen\agent_bridge\.env")

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

def restore_unseen():
    try:
        print(f"Conectando a {IMAP_SERVER} para restaurar misiones...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        # Buscar correos con [BILL-MISSION] que están como leídos (\Seen)
        # Buscamos los recibidos hoy para no re-procesar cosas muy viejas
        status, messages = mail.search(None, '(SUBJECT "[BILL-MISSION]")')
        
        if status == "OK" and messages[0]:
            mail_ids = messages[0].split()
            print(f"Encontrados {len(mail_ids)} correos con [BILL-MISSION]. Restaurando estado UNSEEN...")
            
            for num in mail_ids:
                # Quitar el flag \Seen para que vuelvan a aparecer como nuevos
                mail.store(num, '-FLAGS', '\\Seen')
            
            print("✅ Misiones restauradas exitosamente.")
        else:
            print("No se encontraron correos para restaurar.")

        mail.logout()
    except Exception as e:
        print(f"Error al restaurar: {e}")

if __name__ == "__main__":
    restore_unseen()
