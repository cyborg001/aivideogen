import os
import shutil
import glob

# Rutas configuradas
BRAIN_DIR = r"C:\Users\hp\.gemini\antigravity\brain\e36530f5-3e59-4166-8092-71222238d314"
ASSETS_DIR = r"c:\Users\hp\aivideogen\aivideogen\media\assets\cyborg001"

def sync_assets():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR)
        print(f"📁 Carpeta creada: {ASSETS_DIR}")

    # Patrones de imagen
    extensions = ['*.png', '*.jpg', '*.jpeg', '*.webp']
    files_to_sync = []
    for ext in extensions:
        files_to_sync.extend(glob.glob(os.path.join(BRAIN_DIR, ext)))

    print(f"--- Buscando imagenes en el Cerebro: {len(files_to_sync)} encontradas.")

    for src_path in files_to_sync:
        filename = os.path.basename(src_path)
        
        # Limpieza básica de nombres (ej: quitar timestamps)
        import re
        clean_name = re.sub(r'_\d{10,}\.', '.', filename)
        
        dst_path = os.path.join(ASSETS_DIR, clean_name)
        
        if not os.path.exists(dst_path):
            try:
                shutil.copy2(src_path, dst_path)
                print(f"OK - Sincronizado: {clean_name}")
            except Exception as e:
                print(f"ERROR - al copiar {filename}: {e}")
        else:
            # Si el archivo ya existe, verificamos si es más reciente
            if os.path.getmtime(src_path) > os.path.getmtime(dst_path):
                shutil.copy2(src_path, dst_path)
                print(f"UPD - Actualizado: {clean_name}")
            else:
                pass # Ya está al día

    print("\nSincronizacion completada.")

if __name__ == "__main__":
    sync_assets()
