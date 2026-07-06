import os
import random
import subprocess
import re

# Set random seed for reproducibility of specific runs
random.seed(101)

output_dir = r'C:\Users\hp\aivideogen\fisica'
edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

# Theoretical questions (remain constant, but are shuffled)
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

# Generators for parameterized problems
def gen_p1():
    # Sum of 2D vectors
    # Avoid original values (1.50, 1.60) & (2.50, 1.40)
    f1x = round(random.uniform(1.1, 3.9), 2)
    f1y = round(random.uniform(1.1, 3.9), 2)
    f2x = round(random.uniform(1.1, 4.9), 2)
    f2y = round(random.uniform(1.1, 4.9), 2)
    
    rx = round(f1x + f2x, 2)
    ry = round(f1y + f2y, 2)
    
    text = f"Una partícula recibe la acción de dos fuerzas coplanares: $\\vec{{F}}_1 = ({f1x:.2f} \\text{{ N}}, {f1y:.2f} \\text{{ N}})$ y $\\vec{{F}}_2 = ({f2x:.2f} \\text{{ N}}, {f2y:.2f} \\text{{ N}})$. Determine las componentes de la fuerza neta:"
    ans = f"$({rx:.2f} \\text{{ N}}, {ry:.2f} \\text{{ N}})$"
    
    opts = [
        ans,
        f"$({ry:.2f} \\text{{ N}}, {rx:.2f} \\text{{ N}})$",
        f"$({(rx-0.5):.2f} \\text{{ N}}, {(ry+0.5):.2f} \\text{{ N}})$",
        f"$({(rx+1.0):.2f} \\text{{ N}}, {(ry-1.0):.2f} \\text{{ N}})$"
    ]
    random.shuffle(opts)
    
    calc = f"Sumamos las componentes correspondientes: $F_x = {f1x:.2f} + {f2x:.2f} = {rx:.2f}\\text{{ N}}$ y $F_y = {f1y:.2f} + {f2y:.2f} = {ry:.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p2():
    # Magnitude of net force (using Pythagorean triples to get integers)
    # Triples: (3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15)
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (9, 12, 15)]
    tx, ty, tr = random.choice(triples)
    
    # Split tx and ty into two parts randomly
    f1x = round(random.uniform(1.0, tx - 1.0), 2)
    f2x = round(tx - f1x, 2)
    f1y = round(random.uniform(1.0, ty - 1.0), 2)
    f2y = round(ty - f1y, 2)
    
    text = f"Determine la magnitud de la fuerza neta sobre una partícula que recibe la acción de las fuerzas $\\vec{{F}}_1 = ({f1x:.2f} \\text{{ N}}, {f1y:.2f} \\text{{ N}})$ y $\\vec{{F}}_2 = ({f2x:.2f} \\text{{ N}}, {f2y:.2f} \\text{{ N}})$:"
    ans = f"${tr:.2f} \\text{{ N}}$"
    
    opts = [
        ans,
        f"${(tr + 4.0):.2f} \\text{{ N}}$",
        f"${(tr - 2.0):.2f} \\text{{ N}}$",
        f"${(f1x+f2x+f1y+f2y):.2f} \\text{{ N}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Primero sumamos las fuerzas: $\\vec{{F}}_{{\\text{{neta}}}} = ({f1x:.2f}+{f2x:.2f}, {f1y:.2f}+{f2y:.2f}) = ({tx:.2f}\\text{{ N}}, {ty:.2f}\\text{{ N}})$. Luego, su magnitud es: $F = \\sqrt{{{tx:.2f}^2 + {ty:.2f}^2}} = {tr:.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p3():
    # 1D net force sum
    f1x = -1.0 * round(random.uniform(2.0, 6.0), 2)
    f2x = round(random.uniform(7.0, 12.0), 2)
    f3x = -1.0 * round(random.uniform(3.0, 8.0), 2)
    
    rx = round(f1x + f2x + f3x, 2)
    
    text = f"Un bloque en una superficie horizontal recibe tres fuerzas paralelas al eje $x$: $F_{{1x}} = {f1x:.2f} \\text{{ N}}$, $F_{{2x}} = {f2x:+.2f} \\text{{ N}}$ y $F_{{3x}} = {f3x:.2f} \\text{{ N}}$. Determine el valor de la fuerza neta horizontal:"
    ans = f"${rx:+.2f} \\text{{ N}}$"
    
    opts = [
        ans,
        f"${(-rx):+.2f} \\text{{ N}}$",
        f"${(rx + 5.0):+.2f} \\text{{ N}}$",
        f"${(f1x + f2x - f3x):+.2f} \\text{{ N}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Fuerza neta: $F_{{x}} = ({f1x:.2f}) + ({f2x:+.2f}) + ({f3x:.2f}) = {rx:+.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p4():
    # F = m * a
    m = round(random.uniform(2.5, 6.5), 2)
    a = round(random.uniform(0.8, 2.5), 2)
    f = round(m * a, 2)
    
    text = f"Calcule la magnitud de la fuerza neta que actúa sobre un bloque de masa $m = {m:.2f} \\text{{ kg}}$ si este se mueve con una aceleración constante de {a:.2f} \\text{{ m/s}}^2$:"
    ans = f"${f:.2f} \\text{{ N}}$"
    
    opts = [
        ans,
        f"${(m/a):.2f} \\text{{ N}}$",
        f"${(f + 1.5):.2f} \\text{{ N}}$",
        f"${(f - 0.8):.2f} \\text{{ N}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Aplicamos la segunda ley de Newton: $F = m \\cdot a = {m:.2f} \\text{{ kg}} \\cdot {a:.2f} \\text{{ m/s}}^2 = {f:.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p5():
    # Mass from net force magnitude (Pythagorean triples to ensure clean mass)
    triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13)]
    fx, fy, fr = random.choice(triples)
    a = random.choice([2.00, 2.50, 5.00])
    m = round(fr / a, 2)
    
    text = f"Determine la masa de un cuerpo que se mueve con una aceleración de {a:.2f} \\text{{ m/s}}^2$ sabiendo que la fuerza neta que actúa sobre él es $\\vec{{F}}_{{\\text{{neta}}}} = ({fx:.2f} \\text{{ N}}, {fy:.2f} \\text{{ N}})$:"
    ans = f"${m:.2f} \\text{{ kg}}$"
    
    opts = [
        ans,
        f"${(m + 1.5):.2f} \\text{{ kg}}$",
        f"${(m - 0.8):.2f} \\text{{ kg}}$",
        f"${(fr * a):.2f} \\text{{ kg}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Primero magnitud de la fuerza: $F = \\sqrt{{{fx:.2f}^2 + {fy:.2f}^2}} = {fr:.2f}\\text{{ N}}$. Luego masa: $m = F / a = {fr:.2f} / {a:.2f} = {m:.2f}\\text{{ kg}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p6():
    # Acceleration from 1D forces
    m = round(random.uniform(3.0, 6.0), 2)
    f1x = -1.0 * round(random.uniform(5.0, 10.0), 2)
    f2x = round(random.uniform(11.0, 16.0), 2)
    
    ax = round((f1x + f2x) / m, 3)
    
    text = f"Un bloque de masa $m = {m:.2f} \\text{{ kg}}$ es sometido a dos fuerzas horizontales: $F_{{1x}} = {f1x:.2f} \\text{{ N}}$ y $F_{{2x}} = {f2x:+.2f} \\text{{ N}}$. Determine la componente de su aceleración $a_x$:"
    ans = f"${ax:+.3f} \\text{{ m/s}}^2$"
    
    opts = [
        ans,
        f"${(-ax):+.3f} \\text{{ m/s}}^2$",
        f"${(ax * 1.5):+.3f} \\text{{ m/s}}^2$",
        f"${(f2x/m):+.3f} \\text{{ m/s}}^2$"
    ]
    random.shuffle(opts)
    
    calc = f"Fuerza neta horizontal: $F_{{x}} = {f1x:.2f} + {f2x:+.2f} = {(f1x+f2x):+.2f}\\text{{ N}}$. Aceleración: $a_x = F_x / m = {(f1x+f2x):+.2f} / {m:.2f} = {ax:+.3f}\\text{{ m/s}}^2$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p7():
    # Find force component from acceleration
    m = round(random.uniform(2.5, 4.5), 2)
    ax = round(random.uniform(0.5, 1.5), 2)
    f2x = round(random.uniform(6.0, 11.0), 2)
    
    f1x = round(m * ax - f2x, 2)
    
    text = f"Un cuerpo de masa $m = {m:.2f} \\text{{ kg}}$ acelera horizontalmente a razón de $a_x = +{ax:.2f} \\text{{ m/s}}^2$. Si actúan dos fuerzas sobre el eje $x$ y una de ellas es $F_{{2x}} = +{f2x:.2f} \\text{{ N}}$, determine la componente de la otra fuerza $F_{{1x}}$:"
    ans = f"${f1x:.2f} \\text{{ N}}$"
    
    opts = [
        ans,
        f"${(-f1x):.2f} \\text{{ N}}$",
        f"${(f1x - 3.0):.2f} \\text{{ N}}$",
        f"${(m * ax + f2x):.2f} \\text{{ N}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Fuerza neta: $F_x = m \\cdot a_x = {m:.2f} \\cdot {ax:.2f} = {(m*ax):.2f}\\text{{ N}}$. Despejando: $F_{{1x}} = F_x - F_{{2x}} = {(m*ax):.2f} - {f2x:.2f} = {f1x:.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p8():
    # Hard problem 1: Deceleration of car (converting km/h to m/s)
    # Pick speeds that convert to clean m/s
    # 72 km/h -> 20 m/s; 36 km/h -> 10 m/s; 90 km/h -> 25 m/s; 54 km/h -> 15 m/s; 18 km/h -> 5 m/s
    pairs = [(72, 36, 20.0, 10.0), (90, 54, 25.0, 15.0), (54, 18, 15.0, 5.0), (72, 18, 20.0, 5.0)]
    v0_kmh, v_kmh, v0_ms, v_ms = random.choice(pairs)
    t = random.choice([3.00, 4.00, 5.00])
    
    dx = round(((v0_ms + v_ms) / 2.0) * t, 2)
    
    text = f"Un automóvil que viaja en línea recta a {v0_kmh:.1f} \\text{{ km/h}} ({v0_ms:.1f} \\text{{ m/s}}) pisa los frenos durante {t:.2f} \\text{{ s}} reduciendo su velocidad de forma uniforme hasta {v_kmh:.1f} \\text{{ km/h}} ({v_ms:.1f} \\text{{ m/s}}). Calcule la distancia recorrida ($\\Delta x$) durante el frenado:"
    ans = f"${dx:.2f} \\text{{ m}}$"
    
    opts = [
        ans,
        f"${(dx + 12.0):.2f} \\text{{ m}}$",
        f"${(dx - 8.5):.2f} \\text{{ m}}$",
        f"${(v0_ms * t):.2f} \\text{{ m}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Fórmula de MRUV: $\\Delta x = \\frac{{v_0 + v}}{{2}} \\cdot t = \\frac{{{v0_ms:.1f} + {v_ms:.1f}}}{{2}} \\cdot {t:.2f} = {dx:.2f}\\text{{ m}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p9():
    # MRUV displacement from rest
    v0 = round(random.uniform(1.0, 3.0), 2)
    a = round(random.uniform(1.5, 3.5), 2)
    t = random.choice([2.00, 3.00, 4.00])
    
    dx = round(v0 * t + 0.5 * a * (t**2), 2)
    
    text = f"Una caja se desliza por una rampa inclinada con una aceleración constante de {a:.2f} \\text{{ m/s}}^2$ partiendo con una velocidad inicial de {v0:.2f} \\text{{ m/s}}. Calcule el desplazamiento de la caja al cabo de {t:.2f} \\text{{ s}}$:"
    ans = f"${dx:.2f} \\text{{ m}}$"
    
    opts = [
        ans,
        f"${(dx + 5.0):.2f} \\text{{ m}}$",
        f"${(dx - 3.5):.2f} \\text{{ m}}$",
        f"${(v0 * t):.2f} \\text{{ m}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Fórmula de MRUV: $\\Delta x = v_0 t + \\frac{{1}}{{2}} a t^2 = {v0:.2f}({t:.2f}) + 0.5({a:.2f})({t:.2f})^2 = {dx:.2f}\\text{{ m}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p10():
    # Hard problem 2: Acceleration of golf ball
    v0 = round(random.uniform(5.0, 8.0), 2)
    v = round(random.uniform(1.0, 3.0), 2)
    dx = round(random.uniform(8.0, 15.0), 2)
    
    a = round((v**2 - v0**2) / (2.0 * dx), 2)
    
    text = f"Una bola de golf se desliza por el césped con una velocidad inicial de {v0:.2f} \\text{{ m/s}} y llega al hoyo a {v:.2f} \\text{{ m/s}} después de recorrer una distancia de {dx:.2f} \\text{{ m}} en línea recta. Determine su aceleración constante:"
    ans = f"${a:.2f} \\text{{ m/s}}^2$"
    
    opts = [
        ans,
        f"${(-a):.2f} \\text{{ m/s}}^2$",
        f"${(a * 1.5):.2f} \\text{{ m/s}}^2$",
        f"${(a - 0.5):.2f} \\text{{ m/s}}^2$"
    ]
    random.shuffle(opts)
    
    calc = f"Usamos la relación $v^2 = v_0^2 + 2 a \\Delta x \\implies a = \\frac{{v^2 - v_0^2}}{{2 \\Delta x}} = \\frac{{{v:.2f}^2 - {v0:.2f}^2}}{{2({dx:.2f})}} = {a:.2f}\\text{{ m/s}}^2$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p11():
    # Free Fall height
    t = round(random.uniform(1.2, 2.2), 2)
    g = 9.80
    h = round(0.5 * g * (t**2), 2)
    
    text = f"Un estudiante deja caer un objeto (desde el reposo) desde la azotea de un edificio y mide que tarda exactamente {t:.2f} \\text{{ s}} en golpear el suelo. Despreciando la resistencia del aire y usando $g = 9.80 \\text{{ m/s}}^2$, calcule la altura del edificio:"
    ans = f"${h:.2f} \\text{{ m}}$"
    
    opts = [
        ans,
        f"${(h + 6.0):.2f} \\text{{ m}}$",
        f"${(h - 4.5):.2f} \\text{{ m}}$",
        f"${(g * t):.2f} \\text{{ m}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Altura en caída libre desde reposo: $h = \\frac{{1}}{{2}} g t^2 = 0.5(9.80)({t:.2f})^2 = {h:.2f}\\text{{ m}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p12():
    # Friction force
    n = round(random.uniform(5.0, 15.0), 2)
    muc = round(random.uniform(0.12, 0.35), 3)
    fc = round(muc * n, 2)
    
    text = f"Determine la magnitud de la fuerza de fricción cinética que actúa sobre un bloque que se desliza por el suelo horizontal, si la fuerza normal de la superficie sobre él es $n = {n:.2f} \\text{{ N}}$ y el coeficiente de fricción cinético es $\\mu_c = {muc:.3f}$:"
    ans = f"${fc:.2f} \\text{{ N}}$"
    
    opts = [
        ans,
        f"${(n / muc):.2f} \\text{{ N}}$",
        f"${(fc + 1.20):.2f} \\text{{ N}}$",
        f"${(fc - 0.40):.2f} \\text{{ N}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Fórmula de fricción cinética: $f_c = \\mu_c \\cdot n = {muc:.3f} \\cdot {n:.2f} = {fc:.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p13():
    # Weight on moon/planet
    w_earth = round(random.uniform(10.0, 25.0), 1)
    g_local = round(random.uniform(1.2, 3.8), 2)
    g_earth = 9.80
    
    m = w_earth / g_earth
    w_local = round(m * g_local, 2)
    
    text = f"Un cuerpo pesa {w_earth:.1f} \\text{{ N}} en la Tierra ($g = 9.80 \\text{{ m/s}}^2$). ¿Cuánto pesará este mismo cuerpo en la superficie de un asteroide donde la aceleración de la gravedad es de {g_local:.2f} \\text{{ m/s}}^2$?"
    ans = f"${w_local:.2f} \\text{{ N}}$"
    
    opts = [
        ans,
        f"${w_earth:.1f} \\text{{ N}}$",
        f"${(w_local + 4.5):.2f} \\text{{ N}}$",
        f"${(w_earth / g_local):.2f} \\text{{ N}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Masa del cuerpo: $m = W_E / g_E = {w_earth:.1f} / 9.80 = {m:.4f}\\text{{ kg}}$. Peso local: $W_L = m \\cdot g_L = {m:.4f} \\cdot {g_local:.2f} = {w_local:.2f}\\text{{ N}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p14():
    # Hard problem 3: Ferris wheel speed
    d = random.choice([120, 140, 160, 180])
    t_min = random.choice([20.0, 25.0, 30.0, 35.0])
    
    r = d / 2.0
    t_sec = t_min * 60.0
    v = round((2 * 3.14159265 * r) / t_sec, 3)
    
    text = f"Una cápsula de pasajeros en una rueda de la fortuna de {d} \\text{{ m}} de diámetro gira a rapidez constante y le toma exactamente {t_min:.1f} \\text{{ minutos}} ({int(t_sec)} \\text{{ s}}) completar una vuelta entera. Calcule su rapidez lineal:"
    ans = f"${v:.3f} \\text{{ m/s}}$"
    
    opts = [
        ans,
        f"${(v * 2.0):.3f} \\text{{ m/s}}$",
        f"${(v / 2.0):.3f} \\text{{ m/s}}$",
        f"${(d / t_min):.3f} \\text{{ m/s}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Radio $R = D/2 = {r:.1f}\\text{{ m}}$. Período $T = {t_min:.1f} \\cdot 60 = {int(t_sec)}\\text{{ s}}$. Rapidez lineal: $v = \\frac{{2 \\pi R}}{{T}} = \\frac{{2 \\cdot 3.1416 \\cdot {r:.1f}}}{{{int(t_sec)}}} = {v:.3f}\\text{{ m/s}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

def gen_p15():
    # MCU angular velocity
    turns = random.choice([30, 45, 60, 75])
    t = round(random.uniform(1.8, 3.5), 2)
    
    f = turns / t
    omega = round(2 * 3.14159265 * f, 1)
    
    text = f"Un estudiante mide que las aspas de un ventilador realizan exactamente {turns} \\text{{ vueltas}} en un intervalo de {t:.2f} \\text{{ s}}. Calcule la velocidad angular $\\omega$ del ventilador en rad/s (utilice $\\pi \\approx 3.14$):"
    ans = f"${omega:.1f} \\text{{ rad/s}}$"
    
    opts = [
        ans,
        f"${(omega * 2.0):.1f} \\text{{ rad/s}}$",
        f"${(turns / t):.1f} \\text{{ rad/s}}$",
        f"${(omega - 20.0):.1f} \\text{{ rad/s}}$"
    ]
    random.shuffle(opts)
    
    calc = f"Frecuencia $f = N/t = {turns}/{t:.2f} = {f:.2f}\\text{{ Hz}}$. Velocidad angular: $\\omega = 2 \\pi f = 2 \\cdot 3.14 \\cdot {f:.2f} = {omega:.1f}\\text{{ rad/s}}$."
    return {"text": text, "opts": opts, "ans": ans, "calc": calc}

# Database list of problem generators
# 1-7, 9, 11, 12, 13, 15 are easy/medium
# 8, 10, 14 are hard
problem_generators = {
    1: gen_p1,
    2: gen_p2,
    3: gen_p3,
    4: gen_p4,
    5: gen_p5,
    6: gen_p6,
    7: gen_p7,
    8: gen_p8,
    9: gen_p9,
    10: gen_p10,
    11: gen_p11,
    12: gen_p12,
    13: gen_p13,
    14: gen_p14,
    15: gen_p15
}

def format_exam_md(version_name, selected_questions, selected_problems):
    md = f"""# Segundo Parcial de Física Básica - Versión {version_name}

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
    \textbf{\Large SEGUNDO PARCIAL DE FÍSICA BÁSICA} \\[0.2cm]
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
    
    # 3 hard problems generators
    hard_ids = [8, 10, 14]
    # Remaining 12 easy/medium problem generators
    easy_med_ids = [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 15]
    
    solucionario_md = "# Solucionario de Exámenes de Segundo Parcial (Versiones A, B, C)\n\n"
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
    \textbf{\large Segundo Parcial de Física Básica - Versiones A, B, C} \\[0.4cm]
\end{center}

\hrule
\vspace{0.4cm}
"""

    for i, v in enumerate(versions):
        # 1. Select 8 random theory questions
        v_questions = random.sample(questions, 8)
        
        # 2. Select problems: 1 hard generator + 3 random easy/medium generators
        hard_id = hard_ids[i]  # A gets 8, B gets 10, C gets 14
        v_easy_med_ids = random.sample(easy_med_ids, 3)
        
        # Instantiate the generators to create unique problems for this version!
        v_problems = []
        # Add the hard one
        v_problems.append(problem_generators[hard_id]())
        # Add the easy/medium ones
        for pid in v_easy_med_ids:
            v_problems.append(problem_generators[pid]())
            
        # Shuffle the instantiated problems list
        random.shuffle(v_problems)
        
        # Format files
        md_content = format_exam_md(v, v_questions, v_problems)
        tex_content = format_exam_tex(v, v_questions, v_problems)
        
        md_file = os.path.join(output_dir, f'segundo_parcial_version_{v.lower()}.md')
        tex_file = os.path.join(output_dir, f'segundo_parcial_version_{v.lower()}.tex')
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(tex_content)
            
        print(f"Generated Version {v} files with UNIQUE values.")
        
        # MD Solucionario
        solucionario_md += f"## Examen Versión {v}\n\n"
        solucionario_md += "### I. Teoría\n"
        for idx, q in enumerate(v_questions, 1):
            solucionario_md += f"{idx}. **Respuesta:** {q['ans']} (Pregunta: *{q['text']}*)\n"
            
        solucionario_md += "\n### II. Problemas Prácticos\n"
        for idx, p in enumerate(v_problems, 1):
            solucionario_md += f"{idx}. **Respuesta:** {p['ans']}\n"
            solucionario_md += f"   * *Problema:* {p['text']}\n"
            solucionario_md += f"   * *Cálculo:* {p['calc']}\n"
        solucionario_md += "\n---\n\n"
        
        # TeX Solucionario
        solucionario_tex += r"\subsection*{Examen Versión " + v + r"}"
        solucionario_tex += r"\textbf{I. Teoría:}"
        solucionario_tex += r"\begin{enumerate}"
        for q in v_questions:
            solucionario_tex += f"    \\item \\textbf{{Respuesta:}} {q['ans']} \\\\ \\textit{{{q['text']}}}\n"
        solucionario_tex += r"\end{enumerate}"
        
        solucionario_tex += r"\textbf{II. Problemas Prácticos:}"
        solucionario_tex += r"\begin{enumerate}"
        for p in v_problems:
            solucionario_tex += f"    \\item \\textbf{{Respuesta:}} {p['ans']} \\\\\n"
            solucionario_tex += f"    \\textit{{{p['text']}}} \\\\\n"
            solucionario_tex += f"    \\textbf{{Desarrollo:}} {p['calc']}\n"
        solucionario_tex += r"\end{enumerate}"
        solucionario_tex += r"\vspace{0.4cm} \hrule \vspace{0.4cm}"

    solucionario_tex += r"\end{document}"
    
    # Save Solucionarios
    sol_md_file = os.path.join(output_dir, 'solucionario_segundo_parcial.md')
    sol_tex_file = os.path.join(output_dir, 'solucionario_segundo_parcial.tex')
    
    with open(sol_md_file, 'w', encoding='utf-8') as f:
        f.write(solucionario_md)
    with open(sol_tex_file, 'w', encoding='utf-8') as f:
        f.write(solucionario_tex)
        
    print("Generated Solucionario files with UNIQUE development keys.")

def compile_all_pdfs():
    files = ["segundo_parcial_version_a", "segundo_parcial_version_b", "segundo_parcial_version_c", "solucionario_segundo_parcial"]
    
    for filename in files:
        md_file = os.path.join(output_dir, f"{filename}.md")
        html_file = os.path.join(output_dir, f"{filename}.html")
        pdf_file = os.path.join(output_dir, f"{filename}.pdf")
        
        print(f"Compiling {filename} to PDF...")
        
        # Read MD
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
            
        # Parse simple HTML (reusing our compilation script logic)
        title_tag = "Segundo Parcial de Física Básica" if "version" in filename else "Solucionario Oficial - Segundo Parcial"
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
                q_text = re.sub(r'\*\frac', r'\\frac', q_text) # Fix double escaping in regex if any
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
