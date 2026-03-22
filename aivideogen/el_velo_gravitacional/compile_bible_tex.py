import re
import os

def biblia_to_latex(md_file, tex_file):
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found.")
        return

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert markdown to LaTeX
    # Headers
    content = re.sub(r'^# (.+)$', r'\\chapter{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.+)$', r'\\section*{\1}', content, flags=re.MULTILINE)
    content = re.sub(r'^### (.+)$', r'\\subsection*{\1}', content, flags=re.MULTILINE)
    
    # Bold
    content = re.sub(r'\*\*([^*]+)\*\*', r'\\textbf{\1}', content)
    
    # Italics
    content = re.sub(r'\*([^*]+)\*', r'\\textit{\1}', content)
    
    # Em-dashes
    content = re.sub(r'—', r'---', content)
    
    # Lists
    content = re.sub(r'^- (.+)$', r'\\begin{itemize}\n  \\item \1\n\\end{itemize}', content, flags=re.MULTILINE)
    # Fix nested itemize (very simple fix)
    content = content.replace('\\end{itemize}\n\\begin{itemize}', '')

    # LaTeX header
    header = r'''\documentclass[12pt,a4paper]{report}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{setspace}
\onehalfspacing
\usepackage{hyperref}

\title{\textbf{Biblia del Universo}\\[0.5cm]\large El Velo Gravitacional}
\author{Carlos G. Ramirez}
\date{31 de diciembre de 2025}

\begin{document}

\maketitle
\tableofcontents
\newpage

'''
    
    footer = r'''
\end{document}
'''
    
    # Write output
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(header + content + footer)
    
    print(f"Converted {md_file} to {tex_file}")

if __name__ == "__main__":
    biblia_to_latex("biblia_del_universo.md", "BIBLIA_DEL_UNIVERSO.tex")
