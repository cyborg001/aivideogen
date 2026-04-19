
import shutil
import os

# Rutas de Origen (Bill's Brain)
source_dir = r"C:\Users\hp\.gemini\antigravity\brain\35817659-2cc8-45e6-83d3-cbb3266e6ede"
assets = [
    "miniatura_bloqueo_naval_epic_fury_1776573355570.png",
    "miniatura_bloqueo_naval_click_king_1776573835278.png",
    "miniatura_bloqueo_naval_trump_khamenei_confrontation_1776574262217.png",
    "miniatura_bloqueo_naval_master_16_9_1776574448333.png"
]

# Ruta de Destino (Proyecto Geopolítico)
dest_dir = r"c:\Users\hp\aivideogen\aivideogen\media\assets\investigacion"

def deploy():
    print("--- Iniciando Despliegue de Activos Visuales ---")
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Creado directorio: {dest_dir}")

    for asset in assets:
        src = os.path.join(source_dir, asset)
        # Nombre de destino simplificado
        clean_name = asset.split('_177')[0] + ".png" 
        dst = os.path.join(dest_dir, clean_name)
        
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"✅ Desplegado: {clean_name}")
        else:
            print(f"❌ Error: No se encontró el origen {asset}")

    print("\n--- Operación Completada con Éxito ---")

if __name__ == "__main__":
    deploy()
