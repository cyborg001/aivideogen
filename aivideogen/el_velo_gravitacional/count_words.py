import os

def count_words(filepath):
    if not os.path.exists(filepath):
        return 0
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        # Simple word count: split by whitespace
        return len(content.split())

directory = r'c:\Users\Usuario\Documents\curso creacion contenido con ia\libros\el_velo_gravitacional'
files = [
    'prologo_el_regalo.md',
    'capitulo_1_primeros_pasos.md',
    'capitulo_2_el_circulo.md',
    'capitulo_3_el_viejo_toro.md',
    'capitulo_4_el_peso_de_la_gravedad.md',
    'capitulo_5_chispas_en_el_oxido.md',
    'capitulo_6_el_velo_gravitacional.md',
    'biblia_del_universo.md'
]

compiled_files = [
    'COMPILADO_libro_completo.md',
    'COMPILADO_libro_completo.tex',
    'COMPILADO_libro_PROFESIONAL.tex',
    'BIBLIA_DEL_UNIVERSO.tex'
]

print("Individual Files:")
total_individual = 0
for f in files:
    path = os.path.join(directory, f)
    count = count_words(path)
    print(f"{f}: {count} words")
    total_individual += count
print(f"Total individual files: {total_individual} words")

print("\nCompiled Files:")
for f in compiled_files:
    path = os.path.join(directory, f)
    count = count_words(path)
    print(f"{f}: {count} words")
