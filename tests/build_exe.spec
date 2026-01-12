# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# Copy metadata for packages that use importlib.metadata
datas_metadata = copy_metadata('imageio')
datas_metadata += copy_metadata('moviepy')
datas_metadata += copy_metadata('decorator')
datas_metadata += copy_metadata('proglog')

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('generator', 'generator'),
        ('researcher', 'researcher'),
        ('media', 'media'),
        ('docs', 'docs'),
        ('README.txt', '.'),
        ('.env.example', '.'),
        ('db.sqlite3', '.'),
    ] + datas_metadata,
    hiddenimports=[
        'django',
        'django.contrib.staticfiles',
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.sessions',
        'django.contrib.messages',
        'moviepy',
        'moviepy.video',
        'moviepy.audio',
        'moviepy.editor',
        'PIL',
        'numpy',
        'requests',
        'elevenlabs',
        'edge_tts',
        'dotenv',
        'google.generativeai',
        'imageio',
        'imageio.plugins',
        'imageio_ffmpeg',
        'decorator',
        'proglog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_Video_Generator_v2.12.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Video_Generator_v2.12.1',
)
