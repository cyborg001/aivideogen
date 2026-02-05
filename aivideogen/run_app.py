import os
import sys
import webbrowser
import threading
import time
import subprocess
from pathlib import Path
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

# Force UTF-8 and unbuffered output
os.environ['PYTHONUTF8'] = '1'
os.environ['PYTHONUNBUFFERED'] = '1'

# Re-open stdout/stderr with UTF-8 encoding to avoid UnicodeEncodeError in some consoles
import io
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def open_browser(port):
    """Wait for server to start and then open the browser."""
    time.sleep(2.5)
    url = f'http://127.0.0.1:{port}'
    print(f"Abriendo aplicación en {url}...")
    try:
        # Try to open with Chrome --app mode if possible for better look
        import subprocess
        subprocess.Popen(['start', 'chrome', f'--app={url}', '--start-maximized'], shell=True)
    except:
        import webbrowser
        webbrowser.open(url)

def start_gui_control():
    """Opens a small Tkinter window to control the server."""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.title("aiVideoGen Server")
    root.geometry("300x120")
    root.resizable(False, False)
    root.attributes('-topmost', True)
    
    # Custom icon or style could be added here
    label = tk.Label(root, text="El servidor está activo.", font=("Segoe UI", 12, "bold"), pady=10)
    label.pack()
    
    info = tk.Label(root, text="Cierra esta ventana para apagar el servidor.", font=("Segoe UI", 8), fg="gray")
    info.pack()

    def on_closing():
        if messagebox.askokcancel("Apagar", "¿Deseas apagar el servidor de aiVideoGen?"):
            print("Cerrando aplicación por petición del usuario...")
            root.destroy()
            os._exit(0)

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

# OLD monitor_heartbeat removed per user request (v6.1)

if __name__ == "__main__":
    # Load .env variables
    load_dotenv()
    
    # Get configuration
    port = os.getenv('PORT', '8888')
    version = "8.5.0"
    
    print(f"=======================================================")
    print(f"      AIVideogen v{version} - MOTOR DE EVENTOS")
    print(f"=======================================================")
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # IMPORTANT: Ensure the database path is absolute and points to the right place
    import django
    from django.conf import settings
    
    # Path of this script or the EXE
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller temp folder
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).resolve().parent
        
    db_path = base_path / 'db.sqlite3'
    os.environ['DATABASE_PATH'] = str(db_path)
    
    django.setup()
    
    # Start browser in a separate thread
    if os.environ.get('RUN_MAIN') != 'true': # Prevent double opening on reloader
        threading.Thread(target=open_browser, args=(port,)).start()
        # Start GUI control window instead of inactivity monitor
        threading.Thread(target=start_gui_control, daemon=True).start()
    
    print(f"Iniciando AIVideogen en el puerto {port}...")
    if os.environ.get('RUN_MAIN') != 'true':
        print(f"Verifying database integrity at: {db_path}")
        try:
            from django.core.management import call_command
            call_command('migrate', no_input=True, verbosity=1)
            print("Database integrity verified.")
        except Exception as e:
            print(f"Warning: Auto-migration failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run server
    try:
        print(f"Server starting on 127.0.0.1:{port}...")
        # Skip checks to avoid hangs in standalone mode
        # Note: runserver is threaded by default in Django.
        sys.argv = ['manage.py', 'runserver', f'127.0.0.1:{port}', '--noreload', '--skip-checks']
        execute_from_command_line(sys.argv)
    except Exception as e:
        print(f"CRITICAL: Server failed to start: {e}")
        import traceback
        traceback.print_exc()
    except SystemExit as se:
        print(f"CRITICAL: Server exited with code: {se}")
        # If it exited with 1, it might be a port conflict or other error
        if str(se) != "0":
            import traceback
            traceback.print_exc()
    
    print("Application process finished.")
