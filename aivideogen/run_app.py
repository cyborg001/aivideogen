import os
import sys
import webbrowser
import threading
import time
import subprocess
from pathlib import Path
from django.core.management import execute_from_command_line
from dotenv import load_dotenv

# Force unbuffered output for PyInstaller executable
# This ensures that print statements and logs appear immediately in the console
if hasattr(sys, '_MEIPASS'):
    # PyInstaller executable detected
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)
    # Also set environment variable
    os.environ['PYTHONUNBUFFERED'] = '1'

def open_browser(port):
    time.sleep(1.5) # Wait for server to start
    url = f'http://127.0.0.1:{port}'
    
    # Try to open in "App Mode" (Chrome/Edge) for a native feel
    try:
        # Chrome
        subprocess.Popen(['start', 'chrome', f'--app={url}', '--start-maximized'], shell=True)
        return
    except:
        try:
            # Edge
            subprocess.Popen(['start', 'msedge', f'--app={url}', '--start-maximized'], shell=True)
            return
        except:
            pass
            
    # Fallback to default browser
    webbrowser.open(url)

if __name__ == "__main__":
    # Load .env variables
    load_dotenv()
    
    # Get configuration
    port = os.getenv('PORT', '8888')
    version = "3.0.0-ALPHA"
    
    print(f"═══════════════════════════════════════════════════════")
    print(f"      AIVideogen v{version} - MOTOR DE EVENTOS")
    print(f"═══════════════════════════════════════════════════════")
    
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
