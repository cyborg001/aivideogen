import os
import sys
from PyInstaller.__main__ import run
from PyInstaller.utils.hooks import copy_metadata

def build():
    # Define paths
    base_dir = os.getcwd()
    
    # Collect data to include (source, dest)
    datas = [
        ('generator/templates', 'generator/templates'),
        ('researcher/templates', 'researcher/templates'),
        ('generator/static', 'generator/static'), # Added static for CSS/JS
        ('config', 'config'),
        ('docs', 'docs'),
        ('media/overlays', 'media/overlays'),
        ('media/music', 'media/music'), # Added music
        ('media/sfx', 'media/sfx'),     # Added sfx
        ('README.txt', '.'),
        ('VERSIONES.md', '.'),
        ('.env.example', '.'),
        ('manage.py', '.'),
        ('db.sqlite3', '.'), 
        ('favicon.ico', '.'),
    ]
    
    # ... (metadata block omitted for brevity in instruction, keeping same as before) ...
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
        'generator.middleware', # Critical v5.8
        'whitenoise',
    ]

    # Prepare opts
    opts = [
        'run_app.py',
        '--name=AIVideogen_v8.5_Portable',
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

    print("Building executable...")
    run(opts)

    # POST-BUILD
    import shutil
    dist_dir = os.path.join(base_dir, 'dist', 'AIVideogen_v6.0_Portable')
    if os.path.exists(dist_dir):
        # Ensure folders exist
        os.makedirs(os.path.join(dist_dir, 'media', 'assets'), exist_ok=True)
        os.makedirs(os.path.join(dist_dir, 'media', 'videos'), exist_ok=True)
        print("Finalizing distribution: Folders and .env ready.")
        shutil.copy2('.env.example', os.path.join(dist_dir, '.env')) # Create default .env
        print("Done!")

if __name__ == "__main__":
    build()
