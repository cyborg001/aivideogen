import os
import subprocess
import re

md_path = r'C:\Users\hp\aivideogen\fisica\practica_fisica_leyes_y_movimientos.md'
html_path = r'C:\Users\hp\aivideogen\fisica\practica_fisica_leyes_y_movimientos.html'
pdf_path = r'C:\Users\hp\aivideogen\fisica\practica_fisica_leyes_y_movimientos.pdf'
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

def md_to_html(md_content):
    # Simple markdown parser for headers, lists, bold text and math
    html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Práctica de Física Básica: Cinemática y Leyes de Newton</title>
<!-- MathJax for rendering equations -->
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
  },
  svg: {
    fontCache: 'global'
  }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
body {
    font-family: 'Outfit', sans-serif;
    margin: 40px;
    color: #1a1a1a;
    line-height: 1.6;
    font-size: 14px;
}
h1 {
    text-align: center;
    color: #0f172a;
    font-size: 24px;
    font-weight: 700;
    margin-bottom: 5px;
    text-transform: uppercase;
}
.author-info {
    text-align: center;
    color: #64748b;
    font-size: 12px;
    margin-bottom: 30px;
}
h2 {
    color: #1e3a8a;
    font-size: 16px;
    font-weight: 600;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 5px;
    margin-top: 30px;
    margin-bottom: 15px;
}
h3 {
    color: #0f172a;
    font-size: 14px;
    font-weight: 600;
    margin-top: 20px;
    margin-bottom: 10px;
}
hr {
    border: none;
    border-top: 1px dashed #cbd5e1;
    margin: 25px 0;
}
ul, ol {
    margin-left: 20px;
    padding-left: 0;
}
li {
    margin-bottom: 8px;
}
.options-list {
    list-style-type: none;
    padding-left: 15px;
    margin-top: 5px;
}
.options-list li {
    margin-bottom: 4px;
}
. docente {
    color: #475569;
}
@media print {
    body {
        margin: 20px;
    }
    .page-break {
        page-break-before: always;
    }
}
</style>
</head>
<body>
"""

    lines = md_content.split('\n')
    in_list = False
    in_options = False
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        # Headers
        if line_strip.startswith('# '):
            html += f"<h1>{line_strip[2:]}</h1>\n"
            html += f"<div class='author-info'>Autor: Eurípides Herasme Medina / derechos reservados &copy; 2019</div>\n"
        elif line_strip.startswith('## '):
            html += f"<h2>{line_strip[3:]}</h2>\n"
        elif line_strip.startswith('### '):
            html += f"<h3>{line_strip[4:]}</h3>\n"
        elif line_strip.startswith('---'):
            html += "<hr/>\n"
        # List items (questions)
        elif re.match(r'^\d+\.', line_strip):
            # Question item
            match = re.match(r'^(\d+)\.\s+(.*)', line_strip)
            q_num = match.group(1)
            q_text = match.group(2)
            # Parse bold inside question
            q_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', q_text)
            html += f"<p><strong>{q_num}. {q_text}</strong></p>\n"
        # Options list (a, b, c, d)
        elif line_strip.startswith('* '):
            opt_text = line_strip[2:]
            # Parse bold inside option
            opt_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', opt_text)
            html += f"<div class='options-list'>&nbsp;&nbsp;&nbsp;&nbsp;{opt_text}</div>\n"
        else:
            # Paragraph
            # Parse bold
            p_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line_strip)
            html += f"<p>{p_text}</p>\n"

    html += "</body>\n</html>"
    return html

def compile_pdf():
    if not os.path.exists(md_path):
        print(f"Error: md file not found at {md_path}")
        return
        
    print("Reading Markdown content...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    print("Converting Markdown to HTML...")
    html_content = md_to_html(md_content)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Temporary HTML written.")
    
    # Run Edge headless print
    print("Launching Microsoft Edge to print PDF...")
    cmd = [
        edge_path,
        '--headless',
        '--disable-gpu',
        '--no-sandbox',
        f'--print-to-pdf={pdf_path}',
        html_path
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Success! PDF generated successfully at:", pdf_path)
    except Exception as e:
        print("Error compiling PDF via Edge:", e)
    finally:
        # Clean up temporary HTML
        try:
            if os.path.exists(html_path):
                os.remove(html_path)
                print("Temporary HTML cleaned up.")
        except: pass

if __name__ == '__main__':
    compile_pdf()
