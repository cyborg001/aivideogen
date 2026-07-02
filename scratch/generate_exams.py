import os
import random
import subprocess
import re

# Set random seed to ensure reproducible versions (so the answers remain stable)
random.seed(42)

output_dir = r'C:\Users\hp\aivideogen\fisica'
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# Theoretical questions database
questions = [
    {
        "id": 1,
        "text": "La fuerza es una magnitud física de carácter:",
        "opts": ["Escalar.", "Vectorial.", "Adimensional.", "Tensorial de segundo orden."],
        "ans": "Vectorial."
    },
    {
        "id": 2,
        "text": "De acuerdo con la Primera Ley de Newton, si la fuerza neta que actúa sobre un cuerpo es nula, el cuerpo necesariamente:",
        "opts": ["Debe estar en reposo absoluto.", "Permanecerá en reposo o en movimiento rectilíneo uniforme.", "Experimentará un aumento constante de su velocidad.", "Cambiará continuamente su dirección de movimiento."],
        "ans": "Permanecerá en reposo o en movimiento rectilíneo uniforme."
    },
    {
        "id": 3,
        "text": "La Segunda Ley de Newton establece matemáticamente que la aceleración de un cuerpo es:",
        "opts": ["Directamente proporcional a su masa e inversamente proporcional a la fuerza neta.", "Directamente proporcional a la fuerza neta e inversamente proporcional a su masa.", "Independiente de la masa y proporcional al peso.", "Proporcional al cuadrado de la fuerza neta aplicada."],
        "ans": "Directamente proporcional a la fuerza neta e inversamente proporcional a su masa."
    },
    {
        "id": 4,
        "text": "De acuerdo con la Tercera Ley de Newton (Acción-Reacción), si un cuerpo A ejerce una fuerza $\\vec{F}_{AB}$ sobre un cuerpo B, entonces:",
        "opts": [
            "El cuerpo B ejerce sobre A una fuerza de igual magnitud, misma dirección y sentido contrario ($\\vec{F}_{BA} = -\\vec{F}_{AB}$).",
            "El cuerpo B ejerce sobre A una fuerza de mayor magnitud en el mismo sentido.",
            "La fuerza del cuerpo B sobre A es nula porque A inició el contacto.",
            "El cuerpo B ejerce sobre A una fuerza perpendicular a la original."
        ],
        "ans": "El cuerpo B ejerce sobre A una fuerza de igual magnitud, misma dirección y sentido contrario ($\\vec{F}_{BA} = -\\vec{F}_{AB}$)."
    },
    {
        "id": 5,
        "text": "La propiedad física de un cuerpo que mide cuantitativamente su inercia (resistencia al cambio en su estado de movimiento) es la:",
        "opts": ["Aceleración.", "Fuerza normal.", "Masa.", "Fricción."],
        "ans": "Masa."
    },
    {
        "id": 6,
        "text": "En un gráfico de posición en función del tiempo ($x$ vs $t$), la velocidad instantánea en un tiempo determinado equivale a:",
        "opts": ["El área total bajo la curva en ese intervalo.", "La pendiente de la recta secante que corta la curva.", "La pendiente de la recta tangente a la curva en ese punto.", "La longitud del vector de aceleración."],
        "ans": "La pendiente de la recta tangente a la curva en ese punto."
    },
    {
        "id": 7,
        "text": "Con respecto a la fuerza de fricción entre dos superficies secas en contacto, se cumple que:",
        "opts": [
            "El coeficiente de fricción cinética ($\\mu_c$) es siempre menor que el coeficiente de fricción estática ($\\mu_e$).",
            "La fuerza de fricción estática tiene un valor constante e invariable.",
            "La fuerza de fricción es siempre perpendicular a la superficie de contacto.",
            "El coeficiente de fricción depende del área de contacto visible."
        ],
        "ans": "El coeficiente de fricción cinética ($\\mu_c$) es siempre menor que el coeficiente de fricción estática ($\\mu_e$)."
    },
    {
        "id": 8,
        "text": "En un Movimiento Circular Uniforme (MCU), aunque la rapidez es constante, la velocidad cambia de dirección, lo que implica una aceleración centrípeta dirigida hacia:",
        "opts": ["La dirección tangente a la trayectoria circular.", "El centro de la trayectoria circular.", "El sentido opuesto del movimiento lineal.", "El exterior de la circunferencia en dirección radial."],
        "ans": "El centro de la trayectoria circular."
    },
    {
        "id": 9,
        "text": "Despreciando la resistencia del aire, el ángulo de disparo respecto a la horizontal que produce el máximo alcance horizontal para un proyectil es:",
        "opts": ["$30^\\circ$", "$45^\\circ$", "$60^\\circ$", "$90^\\circ$"],
        "ans": "$45^\\circ$"
    },
    {
        "id": 10,
        "text": "A diferencia de la masa, el peso de un objeto:",
        "opts": [
            "Es una propiedad intrínseca que no varía con la gravedad local.",
            "Es la fuerza de atracción gravitatoria que ejerce la Tierra sobre él ($w = m \\cdot g$).",
            "Se mide en kilogramos en el Sistema Internacional.",
            "Es una cantidad escalar pura sin dirección ni sentido."
        ],
        "ans": "Es la fuerza de atracción gravitatoria que ejerce la Tierra sobre él ($w = m \\cdot g$)."
    }
]

# Practical problems database (hard list: 8, 10, 14)
easy_med_problems = [
    {
        "id": 1,
        "text": "Una partícula recibe la acción de dos fuerzas coplanares: $\\vec{F}_1 = (1.50 \\text{ N}, 1.60 \\text{ N})$ y $\\vec{F}_2 = (2.50 \\text{ N}, 1.40 \\text{ N})$. Determine las componentes de la fuerza neta:",
        "opts": ["$(3.00 \\text{ N}, 4.00 \\text{ N})$", "$(4.00 \\text{ N}, 3.00 \\text{ N})$", "$(1.00 \\text{ N}, 0.20 \\text{ N})$", "$(4.00 \\text{ N}, 4.00 \\text{ N})$"],
        "ans": "$(4.00 \\text{ N}, 3.00 \\text{ N})$"
    },
    {
        "id": 2,
        "text": "Determine la magnitud de la fuerza neta sobre una partícula que recibe la acción de las fuerzas $\\vec{F}_1 = (5.00 \\text{ N}, 4.00 \\text{ N})$ y $\\vec{F}_2 = (3.00 \\text{ N}, 2.00 \\text{ N})$:",
        "opts": ["$14.0 \\text{ N}$", "$10.0 \\text{ N}$", "$8.00 \\text{ N}$", "$6.00 \\text{ N}$"],
        "ans": "$10.0 \\text{ N}$"
    },
    {
        "id": 3,
        "text": "Un bloque en una superficie horizontal recibe tres fuerzas paralelas al eje $x$: $F_{1x} = -5.00 \\text{ N}$ (izquierda), $F_{2x} = +9.00 \\text{ N}$ (derecha) y $F_{3x} = -7.00 \\text{ N}$ (izquierda). Determine el valor de la fuerza neta horizontal:",
        "opts": ["$+3.00 \\text{ N}$", "$-3.00 \\text{ N}$", "$+11.0 \\text{ N}$", "$-21.0 \\text{ N}$"],
        "ans": "$-3.00 \\text{ N}$"
    },
    {
        "id": 4,
        "text": "Calcule la magnitud de la fuerza neta que actúa sobre un bloque de masa $m = 4.00 \\text{ kg}$ si este se mueve con una aceleración constante de $1.20 \\text{ m/s}^2$:",
        "opts": ["$3.33 \\text{ N}$", "$4.80 \\text{ N}$", "$5.20 \\text{ N}$", "$0.30 \\text{ N}$"],
        "ans": "$4.80 \\text{ N}$"
    },
    {
        "id": 5,
        "text": "Determine la masa de un cuerpo que se mueve con una aceleración de $2.00 \\text{ m/s}^2$ sabiendo que la fuerza neta que actúa sobre él es $\\vec{F}_{\\text{neta}} = (5.00 \\text{ N}, 7.48 \\text{ N})$:",
        "opts": ["$2.50 \\text{ kg}$", "$4.50 \\text{ kg}$", "$6.24 \\text{ kg}$", "$9.00 \\text{ kg}$"],
        "ans": "$4.50 \\text{ kg}$"
    },
    {
        "id": 6,
        "text": "Un bloque de masa $m = 4.00 \\text{ kg}$ es sometido a dos fuerzas horizontales: $F_{1x} = -8.00 \\text{ N}$ (hacia la izquierda) y $F_{2x} = +10.0 \\text{ N}$ (hacia la derecha). Determine la componente de su aceleración $a_x$:",
        "opts": ["$+0.500 \\text{ m/s}^2$", "$-0.500 \\text{ m/s}^2$", "$+4.50 \\text{ m/s}^2$", "$+2.00 \\text{ m/s}^2$"],
        "ans": "$+0.500 \\text{ m/s}^2$"
    },
    {
        "id": 7,
        "text": "Un cuerpo de masa $m = 3.00 \\text{ kg}$ acelera horizontalmente a razón de $a_x = +0.800 \\text{ m/s}^2$ (hacia la derecha). Si actúan dos fuerzas sobre el eje $x$ y una de ellas es $F_{2x} = +9.00 \\text{ N}$, determine la componente de la otra fuerza $F_{1x}$:",
        "opts": ["$+6.60 \\text{ N}$", "$-6.60 \\text{ N}$", "$-11.4 \\text{ N}$", "$-2.40 \\text{ N}$"],
        "ans": "$-6.60 \\text{ N}$"
    },
    {
        "id": 9,
        "text": "Una caja se desliza por una rampa inclinada con una aceleración constante de $2.00 \\text{ m/s}^2$ partiendo con una velocidad inicial de $1.50 \\text{ m/s}$. Calcule el desplazamiento de la caja al cabo de $3.00 \\text{ s}$:",
        "opts": ["$9.00 \\text{ m}$", "$13.5 \\text{ m}$", "$18.0 \\text{ m}$", "$22.5 \\text{ m}$"],
        "ans": "$13.5 \\text{ m}$"
    },
    {
        "id": 11,
        "text": "Un estudiante deja caer un tomate (desde el reposo) desde la azotea de un edificio y mide que tarda exactamente $1.60 \\text{ s}$ en golpear el suelo. Despreciando la resistencia del aire y usando $g = 9.80 \\text{ m/s}^2$, calcule la altura del edificio:",
        "opts": ["$15.7 \\text{ m}$", "$12.5 \\text{ m}$", "$25.1 \\text{ m}$", "$7.84 \\text{ m}$"],
        "ans": "$12.5 \\text{ m}$"
    },
    {
        "id": 12,
        "text": "Determine la magnitud de la fuerza de fricción cinética que actúa sobre un bloque que se desliza por el suelo horizontal, si la fuerza normal de la superficie sobre él es $n = 8.00 \\text{ N}$ y el coeficiente de fricción cinético es $\\mu_c = 0.200$:",
        "opts": ["$40.0 \\text{ N}$", "$1.60 \\text{ N}$", "$0.025 \\text{ N}$", "$9.80 \\text{ N}$"],
        "ans": "$1.60 \\text{ N}$"
    },
    {
        "id": 13,
        "text": "Un cuerpo pesa $14.7 \\text{ N}$ en la Tierra ($g = 9.80 \\text{ m/s}^2$). ¿Cuánto pesará este mismo cuerpo en la superficie de la Luna, donde la aceleración de la gravedad es de $1.62 \\text{ m/s}^2$?:",
        "opts": ["$14.7 \\text{ N}$", "$2.43 \\text{ N}$", "$23.8 \\text{ N}$", "$1.50 \\text{ N}$"],
        "ans": "$2.43 \\text{ N}$"
    },
    {
        "id": 15,
        "text": "Un estudiante mide que las aspas de un abanico de techo realizan exactamente $40 \\text{ vueltas}$ en un intervalo de $2.50 \\text{ s}$. Calcule la velocidad angular $\\omega$ del abanico en rad/s (utilice $\\pi \\approx 3.14$):",
        "opts": ["$16.0 \\text{ rad/s}$", "$100 \\text{ rad/s}$", "$50.2 \\text{ rad/s}$", "$251 \\text{ rad/s}$"],
        "ans": "$100 \\text{ rad/s}$"
    }
]

hard_problems = [
    {
        "id": 8,
        "text": "Un automóvil que viaja en línea recta a $50.0 \\text{ km/h}$ ($13.9 \\text{ m/s}$) pisa los frenos durante $3.00 \\text{ s}$ reduciendo su velocidad de forma uniforme hasta $18.0 \\text{ km/h}$ ($5.00 \\text{ m/s}$). Calcule la distancia recorrida ($\\Delta x$) durante el frenado:",
        "opts": ["$15.0 \\text{ m}$", "$28.4 \\text{ m}$", "$40.0 \\text{ m}$", "$56.7 \\text{ m}$"],
        "ans": "$28.4 \\text{ m}$"
    },
    {
        "id": 10,
        "text": "Una bola de golf se desliza por el césped con una velocidad inicial de $6.00 \\text{ m/s}$ y llega al hoyo a $2.00 \\text{ m/s}$ después de recorrer una distancia de $10.0 \\text{ m}$ en línea recta. Determine su aceleración constante:",
        "opts": ["$-1.60 \\text{ m/s}^2$", "$+1.60 \\text{ m/s}^2$", "$-3.20 \\text{ m/s}^2$", "$-0.80 \\text{ m/s}^2$"],
        "ans": "$-1.60 \\text{ m/s}^2$"
    },
    {
        "id": 14,
        "text": "Una cápsula de pasajeros en una rueda de la fortuna de $150 \\text{ m}$ de diámetro gira a rapidez constante y le toma exactamente $30.0 \\text{ minutos}$ ($1800 \\text{ s}$) completar una vuelta entera. Calcule su rapidez lineal:",
        "opts": ["$0.524 \\text{ m/s}$", "$0.262 \\text{ m/s}$", "$1.50 \\text{ m/s}$", "$5.00 \\text{ m/s}$"],
        "ans": "$0.262 \\text{ m/s}$"
    }
]

def format_exam_md(version_name, selected_questions, selected_problems):
    md = f"""# Examen Final de Física Básica - Versión {version_name}

**Estudiante:** ______________________________________  **Matrícula:** ______________  
**Fecha:** ________________________  **Calificación:** ______ / 8.0 puntos

---

## I. Teoría (Valor: 4.0 puntos - 0.5 puntos cada una)
*Selecciona la opción correcta en cada una de las siguientes preguntas. No debe haber tachaduras ni enmiendas.*

"""
    for idx, q in enumerate(selected_questions, 1):
        md += f"{idx}. **{q['text']}**\n"
        for opt in q['opts']:
            md += f"   * {opt}\n"
        md += "\n"
        
    md += """---

## II. Problemas Prácticos (Valor: 4.0 puntos - 1.0 punto cada uno)
*Resuelve cada uno de los problemas y selecciona la respuesta correcta. Muestra tus cálculos breves.*

"""
    for idx, p in enumerate(selected_problems, 1):
        md += f"{idx}. **{p['text']}**\n"
        for opt in p['opts']:
            md += f"   * {opt}\n"
        md += "\n"
        
    return md

def format_exam_tex(version_name, selected_questions, selected_problems):
    tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\usepackage{enumerate}
\geometry{top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm}

\begin{document}

\begin{center}
    \textbf{\Large EXAMEN FINAL DE FÍSICA BÁSICA} \\[0.2cm]
    \textbf{\large VERSIÓN """ + version_name + r"""} \\[0.4cm]
\end{center}

\noindent \textbf{Estudiante:} \hrulefill \ \textbf{Matrícula:} \underline{\hspace{3cm}} \\[0.2cm]
\textbf{Fecha:} \underline{\hspace{4cm}} \ \textbf{Calificación:} \underline{\hspace{1.5cm}} / 8.0 puntos \\

\hrule
\section*{I. Teoría (Valor: 4.0 puntos - 0.5 puntos cada una)}
\textit{Selecciona la opción correcta en cada una de las siguientes preguntas. No debe haber tachaduras ni enmiendas.}

\begin{enumerate}
"""
    for q in selected_questions:
        tex += f"    \\item \\textbf{{{q['text']}}}\n"
        tex += "    \\begin{enumerate}[a)]\n"
        for opt in q['opts']:
            # Replace $ formulas if needed or let them be raw TeX since they are already structured in TeX
            tex += f"        \\item {opt}\n"
        tex += "    \\end{enumerate}\n\n"
        
    tex += r"""\end{enumerate}

\hrule
\section*{II. Problemas Prácticos (Valor: 4.0 puntos - 1.0 punto cada uno)}
\textit{Resuelve cada uno de los problemas y selecciona la respuesta correcta. Muestra tus cálculos breves.}

\begin{enumerate}
"""
    for p in selected_problems:
        tex += f"    \\item \\textbf{{{p['text']}}}\n"
        tex += "    \\begin{enumerate}[a)]\n"
        for opt in p['opts']:
            tex += f"        \\item {opt}\n"
        tex += "    \\end{enumerate}\n\n"
        
    tex += r"""\end{enumerate}

\end{document}
"""
    return tex

def build_exams():
    versions = ["A", "B", "C"]
    
    # 3 hard problems distributed among the 3 versions
    hard_assignments = {
        "A": hard_problems[0],
        "B": hard_problems[1],
        "C": hard_problems[2]
    }
    
    solucionario_md = "# Solucionario de Exámenes Finales (Versiones A, B, C)\n\n"
    solucionario_tex = r"""\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[spanish]{babel}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
\usepackage{geometry}
\geometry{top=2.5cm, bottom=2.5cm, left=2.5cm, right=2.5cm}

\begin{document}

\begin{center}
    \textbf{\Large SOLUCIONARIO OFICIAL} \\[0.2cm]
    \textbf{\large Exámenes Finales - Versiones A, B, C} \\[0.4cm]
\end{center}

\hrule
\vspace{0.4cm}
"""

    for v in versions:
        # 1. Selection of 8 random theoretical questions
        v_questions = random.sample(questions, 8)
        
        # 2. Selection of problems: 1 hard problem assigned to this version + 3 random from easy/medium
        v_hard = hard_assignments[v]
        v_easy_med = random.sample(easy_med_problems, 3)
        v_problems = v_easy_med + [v_hard]
        
        # Shuffle the list of problems so the hard one is not always last
        random.shuffle(v_problems)
        
        # Generate Markdown & LaTeX file contents
        md_content = format_exam_md(v, v_questions, v_problems)
        tex_content = format_exam_tex(v, v_questions, v_problems)
        
        md_file = os.path.join(output_dir, f'examen_final_version_{v.lower()}.md')
        tex_file = os.path.join(output_dir, f'examen_final_version_{v.lower()}.tex')
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)
            
        print(f"Generated Version {v} files.")
        
        # Append to solucionario
        solucionario_md += f"## Examen Versión {v}\n\n"
        solucionario_md += "### I. Teoría\n"
        for idx, q in enumerate(v_questions, 1):
            solucionario_md += f"{idx}. **Respuesta:** {q['ans']} (Pregunta: *{q['text']}*)\n"
            
        solucionario_md += "\n### II. Problemas Prácticos\n"
        for idx, p in enumerate(v_problems, 1):
            solucionario_md += f"{idx}. **Respuesta:** {p['ans']} (Problema: *{p['text']}*)\n"
        solucionario_md += "\n---\n\n"
        
        # LaTeX Solucionario
        solucionario_tex += r"\subsection*{Examen Versión " + v + r"}"
        solucionario_tex += r"\textbf{I. Teoría:}"
        solucionario_tex += r"\begin{enumerate}"
        for q in v_questions:
            solucionario_tex += f"    \\item \\textbf{{Respuesta:}} {q['ans']} \\\\ \\textit{{{q['text']}}}\n"
        solucionario_tex += r"\end{enumerate}"
        
        solucionario_tex += r"\textbf{II. Problemas Prácticos:}"
        solucionario_tex += r"\begin{enumerate}"
        for p in v_problems:
            solucionario_tex += f"    \\item \\textbf{{Respuesta:}} {p['ans']} \\\\ \\textit{{{p['text']}}}\n"
        solucionario_tex += r"\end{enumerate}"
        solucionario_tex += r"\vspace{0.4cm} \hrule \vspace{0.4cm}"

    solucionario_tex += r"\end{document}"
    
    # Save Solucionario
    sol_md_file = os.path.join(output_dir, 'solucionario_examenes_finales.md')
    sol_tex_file = os.path.join(output_dir, 'solucionario_examenes_finales.tex')
    
    with open(sol_md_file, 'w', encoding='utf-8') as f:
        f.write(solucionario_md)
    with open(sol_tex_file, 'w', encoding='utf-8') as f:
        f.write(solucionario_tex)
        
    print("Generated Solucionario files.")

def compile_all_pdfs():
    files = ["examen_final_version_a", "examen_final_version_b", "examen_final_version_c", "solucionario_examenes_finales"]
    
    for filename in files:
        md_file = os.path.join(output_dir, f"{filename}.md")
        html_file = os.path.join(output_dir, f"{filename}.html")
        pdf_file = os.path.join(output_dir, f"{filename}.pdf")
        
        print(f"Compiling {filename} to PDF...")
        
        # Read MD
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            
        # Parse simple HTML (reusing our compilation script logic)
        html = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Examen Final de Física Básica</title>
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
    line-height: 1.5;
    font-size: 13px;
}
h1 {
    text-align: center;
    color: #0f172a;
    font-size: 20px;
    font-weight: 700;
    margin-bottom: 25px;
    text-transform: uppercase;
}
h2 {
    color: #1e3a8a;
    font-size: 15px;
    font-weight: 600;
    border-bottom: 1.5px solid #cbd5e1;
    padding-bottom: 3px;
    margin-top: 20px;
    margin-bottom: 10px;
}
h3 {
    color: #0f172a;
    font-size: 13px;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 5px;
}
hr {
    border: none;
    border-top: 1px dashed #cbd5e1;
    margin: 20px 0;
}
ul, ol {
    margin-left: 20px;
    padding-left: 0;
}
li {
    margin-bottom: 6px;
}
.options-list {
    list-style-type: none;
    padding-left: 15px;
    margin-top: 4px;
}
.options-list li {
    margin-bottom: 3px;
}
@media print {
    body {
        margin: 15px;
    }
}
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
            print(f"Generated PDF: {filename}.pdf")
        except Exception as e:
            print(f"Error compiling {filename}: {e}")
        finally:
            if os.path.exists(html_file):
                os.remove(html_file)

if __name__ == '__main__':
    build_exams()
    compile_all_pdfs()
