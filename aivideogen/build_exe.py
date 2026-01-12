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
        ('config', 'config'),
        ('docs', 'docs'),
        ('media/overlays', 'media/overlays'),
        ('README.txt', '.'),
        ('VERSIONES.md', '.'),
        ('.env.example', '.'),
        ('manage.py', '.'),
        ('db.sqlite3', '.'), 
        # Public Documentation from Root
        ('../MANUAL_DE_USUARIO.md', '.'),
        ('../ESTRATEGIA_GUIONES.md', '.'),
    ]
    
    # FIX: Copy metadata for imageio (and others likely needed) to prevent "No package metadata" error
    try:
        datas.extend(copy_metadata('imageio'))
        datas.extend(copy_metadata('tqdm'))
        datas.extend(copy_metadata('requests'))
    except Exception as e:
        print(f"Warning: Could not copy metadata: {e}")
    
    # Define hidden imports (Django often needs help finding these)
    hidden_imports = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'researcher.apps',
        'generator.apps',
        'whitenoise', # If used
    ]

    # Prepare opts
    opts = [
        'run_app.py',
        '--name=AI_Video_Generator_v2.21.5',
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

    # Add metadata (trust copy_metadata but verify existence)
    try:
        # Reduced list to criticals
        for pkg in ['imageio', 'requests', 'tqdm']:
            try:
                meta = copy_metadata(pkg)
                for src, dst in meta:
                    if os.path.exists(src):
                        opts.append(f'--add-data={src}{os.pathsep}{dst}')
                    else:
                        print(f"Warning: Metadata path missing for {pkg}: {src}")
            except Exception as e:
                print(f"Skipping metadata for {pkg}: {e}")
    except Exception as e:
        print(f"Metadata block error: {e}")

    for imp in hidden_imports:
        opts.append(f'--hidden-import={imp}')

    print("Building executable...")
    # print(opts)
    run(opts)

    # POST-BUILD: Copy .env.example to root for visibility
    import shutil
    dist_dir = os.path.join(base_dir, 'dist', 'AI_Video_Generator_v2.21.5')
    if os.path.exists(dist_dir):
        print("Finalizing distribution: Copying .env.example to root...")
        shutil.copy2('.env.example', os.path.join(dist_dir, '.env.example'))
        print("Done!")

if __name__ == "__main__":
    build()
