# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[('generator/templates', 'generator/templates'), ('researcher/templates', 'researcher/templates'), ('config', 'config'), ('docs', 'docs'), ('media/overlays', 'media/overlays'), ('README.txt', '.'), ('VERSIONES.md', '.'), ('.env.example', '.'), ('manage.py', '.'), ('db.sqlite3', '.'), ('../MANUAL_DE_USUARIO.md', '.'), ('../ESTRATEGIA_GUIONES.md', '.'), ('C:\\Python313\\Lib\\site-packages\\imageio-2.37.2.dist-info', 'imageio-2.37.2.dist-info'), ('C:\\Python313\\Lib\\site-packages\\tqdm-4.67.1.dist-info', 'tqdm-4.67.1.dist-info'), ('C:\\Python313\\Lib\\site-packages\\requests-2.32.5.dist-info', 'requests-2.32.5.dist-info'), ('C:\\Python313\\Lib\\site-packages\\imageio-2.37.2.dist-info', 'imageio-2.37.2.dist-info'), ('C:\\Python313\\Lib\\site-packages\\requests-2.32.5.dist-info', 'requests-2.32.5.dist-info'), ('C:\\Python313\\Lib\\site-packages\\tqdm-4.67.1.dist-info', 'tqdm-4.67.1.dist-info')],
    hiddenimports=['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'researcher.apps', 'generator.apps', 'whitenoise'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI_Video_Generator_v2.21.5',
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
    icon=['favicon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI_Video_Generator_v2.21.5',
)
