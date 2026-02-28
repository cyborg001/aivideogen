import os

base_path = r"c:\Users\Usuario\Documents\curso creacion contenido con ia\libros\el_velo_gravitacional"
compiled_path = os.path.join(base_path, "COMPILADO_libro_completo.md")

chapters = [
    "prologo_el_regalo.md",
    "capitulo_1_primeros_pasos.md",
    "capitulo_2_el_circulo.md",
    "capitulo_3_el_viejo_toro.md",
    "capitulo_4_el_peso_de_la_gravedad.md",
    "capitulo_5_chispas_en_el_oxido.md",
    "capitulo_6_el_velo_gravitacional.md"
]

full_content = ""

for i, chapter_file in enumerate(chapters):
    chapter_path = os.path.join(base_path, chapter_file)
    if os.path.exists(chapter_path):
        # Add Part headers for organization
        if i == 1: # Before Chapter 1
            full_content += "\n# PARTE I: EL APRENDIZAJE\n\n"
        elif i == 4: # Before Chapter 4
            full_content += "\n# PARTE II: EL VELO\n\n"
            
        with open(chapter_path, 'r', encoding='utf-8') as f:
            content = f.read()
            full_content += content
            if i < len(chapters) - 1:
                full_content += "\n\n---\n\n"
    else:
        print(f"Warning: {chapter_file} not found.")

with open(compiled_path, 'w', encoding='utf-8') as f:
    f.write(full_content)

print(f"COMPILADO_libro_completo.md updated successfully with all {len(chapters)} components.")
