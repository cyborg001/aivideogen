import os
import sys
from PyInstaller.__main__ import run
from PyInstaller.utils.hooks import copy_metadata

def build():
    # Define paths
    base_dir = os.getcwd()
    
    # Collect data to include (source, dest)
    # PERSONAL SNAPSHOT: Include notiaci and guiones, exclude heavy media
    datas = [
        ('generator/templates', 'generator/templates'),
        ('researcher/templates', 'researcher/templates'),
        ('generator/static', 'generator/static'),
        ('config', 'config'),
        ('docs', 'docs'),
        ('../notiaci', 'notiaci'),   # Corregido: reside un nivel arriba
        ('guiones', 'guiones'),      # Incluimos todos los guiones
        ('README.txt', '.'),
        ('../MANUAL_DE_USUARIO.md', '.'), # Incluimos manual raíz
        ('VERSIONES.md', '.'),
        ('.env', '.'),               # Incluimos el .env real para snapshot personal
        ('manage.py', '.'),
        ('db.sqlite3', '.'), 
        ('favicon.ico', '.'),
    ]
    
    # Metadata and other hooks
    try:
        datas.extend(copy_metadata('imageio'))
        datas.extend(copy_metadata('tqdm'))
        datas.extend(copy_metadata('requests'))
    except Exception as e:
        print(f"Warning: Could not copy metadata: {e}")
    
    # Define hidden imports
    hidden_imports = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'researcher.apps',
        'generator.apps',
        'generator.middleware',
        'whitenoise',
    ]

    # Prepare opts
    opts = [
        'run_app.py',
        '--name=AIVideogen_v8.5_SNAPSHOT_Archi',
        '--onedir',
        '--noconfirm',
        '--clean',
        '--console',
        '--icon=favicon.ico',
    ]

    # Add local data
    for src, dst in datas:
        if os.path.exists(src):
            opts.append(f'--add-data={src}{os.pathsep}{dst}')
        else:
            print(f"skipping local data: {src}")

    for imp in hidden_imports:
        opts.append(f'--hidden-import={imp}')

    print("Building personal SNAPSHOT executable (EXCLUDING MEDIA)...")
    run(opts)

    # POST-BUILD
    import shutil
    dist_dir = os.path.join(base_dir, 'dist', 'AIVideogen_v8.5_SNAPSHOT_Archi')
    if os.path.exists(dist_dir):
        # Ensure media folders exist even if empty
        os.makedirs(os.path.join(dist_dir, 'media', 'assets'), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, 'media', 'videos'), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, 'media', 'music'), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, 'media', 'sfx'), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, 'media', 'overlays'), exist_ok=True)
        
        print("Finalizing SNAPSHOT: Folders ready. Remember to copy your 'media' content manually.")
        # Ensure there is an .env
        if not os.path.exists(os.path.join(dist_dir, '.env')):
            shutil.copy2('.env', os.path.join(dist_dir, '.env'))
        print("Done!")

if __name__ == "__main__":
    build()
