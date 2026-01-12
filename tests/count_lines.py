import os

# Extensiones a contar
extensions = {'.py': 0, '.html': 0, '.css': 0, '.js': 0, '.md': 0}

# Carpetas a excluir
excludes = ['migrations', 'venv', 'env', '__pycache__', 'dist', 'build', '.git', 'node_modules', 'staticfiles']

# Contar líneas
for root, dirs, files in os.walk('.'):
    # Filtrar directorios excluidos
    dirs[:] = [d for d in dirs if d not in excludes and not any(ex in os.path.join(root, d) for ex in excludes)]
    
    for file in files:
        for ext in extensions:
            if file.endswith(ext):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        extensions[ext] += len(f.readlines())
                except:
                    pass

# Calcular total
total = sum(extensions.values())

print("\n" + "="*40)
print("       LÍNEAS DE CÓDIGO")
print("="*40)
print(f"Python (.py):       {extensions['.py']:>8,} líneas")
print(f"HTML (.html):       {extensions['.html']:>8,} líneas")
print(f"CSS (.css):         {extensions['.css']:>8,} líneas")
print(f"JavaScript (.js):   {extensions['.js']:>8,} líneas")
print(f"Markdown (.md):     {extensions['.md']:>8,} líneas")
print("="*40)
print(f"TOTAL:              {total:>8,} líneas")
print("="*40)
