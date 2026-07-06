import os
import subprocess
import re

dir_path = r'C:\Users\hp\aivideogen\fisica'
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# Mapping of old basenames to new basenames
mappings = {
    "examen_final_version_a": "segundo_parcial_version_a",
    "examen_final_version_b": "segundo_parcial_version_b",
    "examen_final_version_c": "segundo_parcial_version_c",
    "solucionario_examenes_finales": "solucionario_segundo_parcial"
}

def rename_and_replace():
    print("Renaming files and updating contents...")
    for old_base, new_base in mappings.items():
        # Handle MD and TEX files
        for ext in ['.md', '.tex']:
            old_file = os.path.join(dir_path, f"{old_base}{ext}")
            new_file = os.path.join(dir_path, f"{new_base}{ext}")
            
            if os.path.exists(old_file):
                print(f"Processing: {old_file} -> {new_file}")
                with open(old_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Perform text replacements
                content = content.replace("Examen Final de Física Básica", "Segundo Parcial de Física Básica")
                content = content.replace("EXAMEN FINAL DE FÍSICA BÁSICA", "SEGUNDO PARCIAL DE FÍSICA BÁSICA")
                content = content.replace("Examen Final", "Segundo Parcial")
                content = content.replace("Exámenes Finales", "Exámenes de Segundo Parcial")
                content = content.replace("solucionario_examenes_finales", "solucionario_segundo_parcial")
                content = content.replace("examen_final", "segundo_parcial")
                
                # Write to the new file
                with open(new_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Delete the old file
                os.remove(old_file)
                print(f"Deleted old file: {old_file}")
            else:
                print(f"Warning: old file not found: {old_file}")

def compile_new_pdfs():
    print("Compiling updated documents to PDF via Edge...")
    for old_base, new_base in mappings.items():
        md_file = os.path.join(dir_path, f"{new_base}.md")
        html_file = os.path.join(dir_path, f"{new_base}.html")
        pdf_file = os.path.join(dir_path, f"{new_base}.pdf")
        
        # Delete old PDF if it exists
        old_pdf = os.path.join(dir_path, f"{old_base}.pdf")
        if os.path.exists(old_pdf):
            os.remove(old_pdf)
            print(f"Deleted old PDF: {old_pdf}")
            
        if not os.path.exists(md_file):
            print(f"Warning: MD file not found: {md_file}")
            continue
            
        print(f"Compiling {new_base} to PDF...")
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            
        # Parse simple HTML (reusing our compilation script logic)
        title_tag = "Segundo Parcial de Física Básica" if "version" in new_base else "Solucionario Oficial - Segundo Parcial"
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title_tag}</title>
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  }},
  svg: {{
    fontCache: 'global'
  }}
}};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
body {{
    font-family: 'Outfit', sans-serif;
    margin: 40px;
    color: #1a1a1a;
    line-height: 1.5;
    font-size: 13px;
}}
h1 {{
    text-align: center;
    color: #0f172a;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 25px;
    text-transform: uppercase;
}}
h2 {{
    color: #1e3a8a;
    font-size: 15px;
    font-weight: 600;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 3px;
    margin-top: 20px;
    margin-bottom: 10px;
}}
h3 {{
    color: #0f172a;
    font-size: 13px;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 5px;
}}
hr {{
    border: none;
    border-top: 1px dashed #cbd5e1;
    margin: 20px 0;
}}
ul, ol {{
    margin-left: 20px;
    padding-left: 0;
}}
li {{
    margin-bottom: 6px;
}}
.options-list {{
    list-style-type: none;
    padding-left: 15px;
    margin-top: 4px;
}}
.options-list li {{
    margin-bottom: 3px;
}}
@media print {{
    body {{
        margin: 15px;
    }}
}}
</style>
</head>
<body>
"""

        lines = md_content.split('\n')
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
                
            if line_strip.startswith('# '):
                html += f"<h1>{line_strip[2:]}</h1>\n"
            elif line_strip.startswith('## '):
                html += f"<h2>{line_strip[3:]}</h2>\n"
            elif line_strip.startswith('### '):
                html += f"<h3>{line_strip[4:]}</h3>\n"
            elif line_strip.startswith('---'):
                html += "<hr/>\n"
            elif re.match(r'^\d+\.', line_strip):
                match = re.match(r'^(\d+)\.\s+(.*)', line_strip)
                q_num = match.group(1)
                q_text = match.group(2)
                q_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', q_text)
                html += f"<p><strong>{q_num}. {q_text}</strong></p>\n"
            elif line_strip.startswith('* '):
                opt_text = line_strip[2:]
                opt_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', opt_text)
                html += f"<div class='options-list'>&nbsp;&nbsp;&nbsp;&nbsp;{opt_text}</div>\n"
            else:
                p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_strip)
                html += f"<p>{p_text}</p>\n"

        html += "</body>\n</html>"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
            
        cmd = [
            edge_path,
            '--headless',
            '--disable-gpu',
            '--no-sandbox',
            f'--print-to-pdf={pdf_file}',
            html_file
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"Generated PDF: {new_base}.pdf")
        except Exception as e:
            print(f"Error compiling {new_base}: {e}")
        finally:
            if os.path.exists(html_file):
                os.remove(html_file)

if __name__ == '__main__':
    rename_and_replace()
    compile_new_pdfs()
    print("Done!")
