import os
import time
import shutil
from datetime import datetime
from dotenv import load_dotenv
import subprocess

# Cargar variables de entorno
load_dotenv()

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INBOX_DIR = os.path.join(BASE_DIR, "inbox")
PROCESSED_DIR = os.path.join(INBOX_DIR, "processed")

if not os.path.exists(PROCESSED_DIR):
    os.makedirs(PROCESSED_DIR)

def notify_wa(message):
    """Llama al script de envío de WhatsApp."""
    try:
        from whatsapp_sender import send_whatsapp_message
        send_whatsapp_message(message)
    except Exception as e:
        print(f"Error al notificar por WhatsApp: {e}")

def process_mission(filename):
    filepath = os.path.join(INBOX_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read().lower()

    print(f"[{datetime.now()}] Procesando misión: {filename}")

    # Inicializar estado de ejecución
    executed = False

    # Lógica de Estatus y Consultas
    if "que hiciste" in content or "qué hiciste" in content or "estatus" in content or "#estatus" in content:
        # Contar misiones en processed
        num_processed = len([f for f in os.listdir(PROCESSED_DIR) if f.endswith(".md")])
        last_missions = sorted([f for f in os.listdir(PROCESSED_DIR) if f.endswith(".md")], reverse=True)[:3]
        mission_list = "\n".join([f"- {m}" for m in last_missions])
        
        notify_wa(f"📊 *Estatus de Bill Centinela*\n\n"
                  f"- Misiones totales procesadas: {num_processed}\n"
                  f"- Últimas acciones:\n{mission_list}\n\n"
                  f"Vigilando inbox cada 30 segundos. Use #noticias, #tesis o #reporte para acciones rápidas.")
        executed = True

    # Lógica de Flags y Palabras Clave (Más flexible con hashtags)
    if "#reporte" in content or ("reporte" in content and "avance" in content):
        print("Ejecutando comando: #reporte")
        subprocess.run(["python", "bill_sender.py", "--whatsapp"])
        executed = True

    if ("noticia" in content or "ciencia" in content or "tecnología" in content) and ("#autorizar" in content or "#noticias" in content):
        print("Ejecutando comando: #investigar_noticias (Autónomo)")
        subprocess.run(["python", "send_news_report.py"])
        executed = True

    if ("tesis" in content or ".md" in content) and ("#autorizar" in content or "#tesis" in content):
        print("Ejecutando comando: #enviar_tesis (Autónomo)")
        subprocess.run(["python", "send_thesis_wa.py"])
        executed = True

    if ("lanzar" in content or "app" in content) and "#autorizar" in content:
        print("Ejecutando comando: #lanzar_app (Autónomo)")
        # Lanzar el batch de la app en un proceso independiente
        batch_path = os.path.join(os.path.dirname(BASE_DIR), "Start_App.bat")
        subprocess.Popen([batch_path], shell=True, cwd=os.path.dirname(BASE_DIR))
        notify_wa("🚀 Bill Centinela: Iniciando AIVideogen v3.0.0-ALPHA en su computadora. El sistema estará operativo en unos segundos. 🫡")
        executed = True

    if "#autorizar" in content and not executed:
        notify_wa("🛡️ Bill Centinela: Bandera #autorizar detectada. He verificado los sistemas y el inbox. Esperando una instrucción específica (Noticias, Tesis, Reporte) o que iniciemos sesión para razonamiento profundo. 🫡")
        executed = True

    if not executed:
        notify_wa(f"📩 Bill: Misión guardada ('{filename}').\n\nSi desea que la ejecute ahora mismo incluya #autorizar + una palabra clave (Reporte, Noticias, Tesis).")
    
    # Mover a procesados
    shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
    print(f"Misión {filename} movida a processed.")

def start_watching():
    print(f"[CENTINELA] Bill Centinela activo. Monitoreando {INBOX_DIR}...")
    while True:
        files = [f for f in os.listdir(INBOX_DIR) if f.startswith("mission_") and f.endswith(".md")]
        for file in files:
            process_mission(file)
        
        time.sleep(30) # Revisar cada 30 segundos

if __name__ == "__main__":
    start_watching()
