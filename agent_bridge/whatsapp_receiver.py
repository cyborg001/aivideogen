from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

INBOX_DIR = "inbox"
AUTHORIZED_WHATSAPP = os.getenv("AUTHORIZED_WHATSAPP")

if not os.path.exists(INBOX_DIR):
    os.makedirs(INBOX_DIR)

@app.route("/whatsapp", methods=['GET', 'POST'])
def whatsapp_reply():
    try:
        """
        Webhook para recibir mensajes de WhatsApp desde Twilio.
        """
        if request.method == 'GET':
            return "Bill Bridge Webhook está activo y esperando misiones (POST). 🫡"

        # Obtener el número del remitente y el cuerpo del mensaje
        from_raw = request.form.get('From', '')
        # Normalizar: eliminar 'whatsapp:', espacios y el signo '+'
        from_number = from_raw.replace('whatsapp:', '').replace(' ', '').replace('+', '').strip()
        body = request.form.get('Body', '')

        target_number = AUTHORIZED_WHATSAPP.replace('+', '').replace(' ', '').strip() if AUTHORIZED_WHATSAPP else None

        print(f"--- DEBUG WHATSAPP ---", flush=True)
        print(f"Bruto: {from_raw}", flush=True)
        print(f"Limpio: {from_number}", flush=True)
        print(f"Esperado (Normalizado): {target_number}", flush=True)
        print(f"Mensaje: {body}", flush=True)
        print(f"-----------------------", flush=True)

        # Verificar autorización
        if target_number and from_number != target_number:
            print(f"Ignorando mensaje de número no autorizado: {from_number} (Esperado: {target_number})", flush=True)
            return str(MessagingResponse())

        print(f"Recibida misión vía WhatsApp de {from_number}: {body[:50]}...", flush=True)

        # Ruta absoluta para el inbox
        base_dir = os.path.dirname(os.path.abspath(__file__))
        abs_inbox_dir = os.path.join(base_dir, INBOX_DIR)
        if not os.path.exists(abs_inbox_dir):
            os.makedirs(abs_inbox_dir)

        # Guardar la misión en el inbox como Markdown
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"mission_wa_{timestamp}.md"
        filepath = os.path.join(abs_inbox_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Misión (WhatsApp): {body[:30]}...\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Remitente: {from_number}\n")
            f.write(f"Canal: WhatsApp\n\n")
            f.write("## Instrucciones Originales\n\n")
            f.write(body)

        # No responder aquí para evitar duplicidad con el Centinela (Watchdog)
        return str(MessagingResponse())

    except Exception as e:
        print(f"!!! ERROR CRITICO EN WHATSAPP_RECEIVER !!!", flush=True)
        print(str(e), flush=True)
        import traceback
        traceback.print_exc()
        return "Internal Server Error", 500

if __name__ == "__main__":
    # Ejecutar en el puerto 5000 (Twilio necesitaría un túnel como ngrok para llegar aquí)
    print("Bill WhatsApp Receiver (Webhook) Iniciado en puerto 5000...")
    app.run(port=5000, debug=True)
