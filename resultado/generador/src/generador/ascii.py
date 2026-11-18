"""Terminal animada: escribe ./kuvex.sh y descifra KUVEX en ASCII."""

import random
from xml.sax.saxutils import escape

from generador.tema import TENUE, TEXTO, VERDE, aparece, ventana

KUVEX = [
    "██╗  ██╗██╗   ██╗██╗   ██╗███████╗██╗  ██╗",
    "██║ ██╔╝██║   ██║██║   ██║██╔════╝╚██╗██╔╝",
    "█████╔╝ ██║   ██║██║   ██║█████╗   ╚███╔╝ ",
    "██╔═██╗ ██║   ██║╚██╗ ██╔╝██╔══╝   ██╔██╗ ",
    "██║  ██╗╚██████╔╝ ╚████╔╝ ███████╗██╔╝ ██╗",
    "╚═╝  ╚═╝ ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝",
]

LINEAS_FINALES = [
    "> web apps · automatizaciones · IA para negocios",
    "> Juan José Ospina · Ingeniería de Sistemas · Medellín",
]

ANCHO, ALTO, CICLO = 860, 340, 12.0
COMANDO = "~$ ./kuvex.sh"
ANCHO_LETRA = 9.6  # a 16 px; textLength lo fuerza igual en cualquier fuente


def _revuelto(linea: str, semilla: int) -> str:
    """Misma silueta con símbolos al azar: el efecto de 'descifrar'."""
    azar = random.Random(semilla)
    return "".join(c if c == " " else azar.choice("@#%&*+=$01") for c in linea)


def _texto(x, y, contenido, color, tamano=16, largo=None, extra=""):
    largo_attr = f' textLength="{largo:.1f}" lengthAdjust="spacingAndGlyphs"' if largo else ""
    return (
        f'<text x="{x}" y="{y}" fill="{color}" font-size="{tamano}" xml:space="preserve"'
        f'{largo_attr} opacity="0">{escape(contenido)}{extra}</text>'
    )


def svg_ascii() -> str:
    partes = []
    # 1) el comando se escribe letra por letra con un recorte que crece
    ancho_cmd = len(COMANDO) * ANCHO_LETRA
    pasos = [(i + 1) * ANCHO_LETRA for i in range(len(COMANDO))]
    t_letra = 0.08
    anchos = "0;" + ";".join(f"{w:.1f}" for w in pasos) + ";0"
    tiempos = "0;" + ";".join(f"{(0.3 + i * t_letra) / CICLO:.4f}" for i in range(len(pasos))) + f";{0.96:.4f}"
    partes.append(
        f'<clipPath id="tecleo"><rect x="30" y="50" height="30" width="0">'
        f'<animate attributeName="width" values="{anchos}" keyTimes="{tiempos}" dur="{CICLO}s" '
        f'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'
    )
    partes.append(
        f'<text x="30" y="70" fill="{VERDE}" font-size="16" xml:space="preserve" clip-path="url(#tecleo)" '
        f'textLength="{ancho_cmd:.1f}" lengthAdjust="spacingAndGlyphs">{escape(COMANDO)}</text>'
    )

    # 2) cada línea de KUVEX sale revuelta y luego se descifra
    tamano, alto_linea = 20, 23
    largo = len(KUVEX[0]) * 12.0
    x = (ANCHO - largo) / 2
    inicio = 0.3 + len(COMANDO) * t_letra + 0.4
    for i, linea in enumerate(KUVEX):
        y = 112 + i * alto_linea
        t = inicio + i * 0.22
        partes.append(_texto(x, y, _revuelto(linea, i), TENUE, tamano, largo, aparece(t, CICLO, t + 0.45)))
        partes.append(_texto(x, y, linea, VERDE, tamano, largo, aparece(t + 0.45, CICLO)))

    # 3) la descripción y el prompt con cursor que parpadea
    t = inicio + len(KUVEX) * 0.22 + 0.7
    for i, linea in enumerate(LINEAS_FINALES):
        partes.append(_texto(30, 270 + i * 24, linea, TEXTO, 15, extra=aparece(t + i * 0.5, CICLO)))
    t_prompt = t + len(LINEAS_FINALES) * 0.5
    partes.append(_texto(30, 322, "~$", VERDE, 16, extra=aparece(t_prompt, CICLO)))
    partes.append(
        f'<rect x="58" y="308" width="10" height="18" fill="{VERDE}" opacity="0">{aparece(t_prompt, CICLO)}'
        f'<animate attributeName="fill-opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>'
    )
    return ventana(ANCHO, ALTO, "juann11@kuvex: ~", "\n".join(partes))
