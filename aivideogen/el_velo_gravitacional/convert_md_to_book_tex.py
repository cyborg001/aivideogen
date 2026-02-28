import re
import sys
import os

def markdown_to_book_latex(md_file, tex_file):
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found.")
        return

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert markdown to LaTeX
    # Parts
    content = re.sub(r'^# PARTE (\w+): (.+)$', r'\\part{\2}', content, flags=re.MULTILINE)
    
    # Chapters
    content = re.sub(r'^# PRÓLOGO: (.+)$', r'\\chapter*{Prólogo: \1}\n\\addcontentsline{toc}{chapter}{Prólogo: \1}\n\\markboth{Prólogo}{Prólogo}', content, flags=re.MULTILINE)
    content = re.sub(r'^# CAPÍTULO (\d+): (.+)$', r'\\chapter{\2}', content, flags=re.MULTILINE)
    
    # Subheaders (dates/locations)
    content = re.sub(r'^## (.+)$', r'\\section*{\1}', content, flags=re.MULTILINE)
    
    # Bold
    content = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', content)
    
    # Italics (non-greedy, no newlines to avoid matching LaTeX commands like \chapter*)
    content = re.sub(r'\*([^*\n]+?)\*', r'\\textit{\1}', content)
    
    # Em-dashes for dialogue (Spanish style)
    content = re.sub(r'—', r'---', content)
    
    # Quotes
    content = re.sub(r'"([^"]+)"', r"``\1''", content)
    
    # Horizontal rules (scene breaks)
    content = re.sub(r'^---$', r'\\bigskip\n\\begin{center}***\\end{center}\n\\bigskip', content, flags=re.MULTILINE)
    
    # Professional Book Header (5.5x8.5in)
    header = r'''\documentclass[11pt,twoside]{book}
\usepackage[utf8]{inputenc}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage[papersize={5.5in,8.5in}, margin=0.75in, bindingoffset=0.25in]{geometry}
\usepackage{setspace}
\onehalfspacing % Un poco de aire para legibilidad
\usepackage{charter} % Una fuente más clásica y legible para libros
\usepackage{bookmark} % Mejora la creación del índice en el PDF
\usepackage{hyperref}

\title{\textbf{El Velo Gravitacional}}
\author{Carlos G. Ramirez}
\date{} % Sin fecha en la portada para mayor limpieza

\begin{document}

\maketitle

\frontmatter
\tableofcontents

\mainmatter

'''
    
    footer = r'''
\end{document}
'''
    
    # Write output
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(header + content + footer)
    
    print(f"Converted {md_file} to {tex_file} (Professional Format)")

if __name__ == "__main__":
    markdown_to_book_latex("COMPILADO_libro_completo.md", "COMPILADO_libro_PROFESIONAL.tex")
