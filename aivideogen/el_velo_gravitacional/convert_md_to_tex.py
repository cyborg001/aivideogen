import re
import sys

def markdown_to_latex(md_file, tex_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content
    
    # Convert markdown to LaTeX
    content = re.sub(r'^# PRÓLOGO: (.+)$', r'\\chapter*{Prólogo: \1}\n\\addcontentsline{toc}{chapter}{Prólogo: \1}', content, flags=re.MULTILINE)
    content = re.sub(r'^# CAPÍTULO (\d+): (.+)$', r'\\chapter{\2}', content, flags=re.MULTILINE)
    content = re.sub(r'^# BIBLIA DEL UNIVERSO$', r'\\appendix\n\\chapter{Biblia del Universo}', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'\\section*{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'\\subsection*{\1}', content, flags=re.MULTILINE)
    
    # Bold
    content = re.sub(r'\*\*FIN DEL (PRÓLOGO|CAPÍTULO \d+)\*\*', r'\\textbf{FIN DEL \1}', content)
    
    # Italics
    content = re.sub(r'\*([^*\n]+)\*', r'\\textit{\1}', content)
    
    # Em-dashes for dialogue
    content = re.sub(r'—', r'---', content)
    
    # Quotes - simpler approach
    content = re.sub(r'"([^"]+)"', r"``\1''", content)
    
    # Horizontal rules
    content = re.sub(r'^---$', r'\\bigskip\n\\noindent\\rule{\\textwidth}{0.4pt}\n\\bigskip', content, flags=re.MULTILINE)
    
    # Escape special LaTeX characters (but not our commands)
    # content = re.sub(r'([&%$#_{}])', r'\\\1', content)
    
    # LaTeX header
    header = r'''\documentclass[12pt,a4paper]{book}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{setspace}
\onehalfspacing
\usepackage{hyperref}

\title{\textbf{El Velo Gravitacional}\\[0.5cm]\large Novela de Ciencia Ficción Hard}
\author{Carlos G. Ramirez}
\date{30 de diciembre de 2025}

\begin{document}

\maketitle
\frontmatter
\tableofcontents
\newpage
\mainmatter

'''
    
    footer = r'''
\end{document}
'''
    
    # Write output
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(header + content + footer)
    
    print(f"Converted {md_file} to {tex_file}")

if __name__ == "__main__":
    markdown_to_latex("COMPILADO_libro_completo.md", "COMPILADO_libro_completo.tex")
