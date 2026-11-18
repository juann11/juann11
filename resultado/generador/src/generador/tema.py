"""Colores y marco de ventana de terminal compartidos por los SVG."""

from xml.sax.saxutils import escape

FONDO = "#0d1117"
BORDE = "#30363d"
TEXTO = "#c9d1d9"
TENUE = "#7d8590"
VERDE = "#39d353"
# los mismos 5 verdes del calendario de GitHub (nivel 0 a 4)
NIVELES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
FUENTE = "'JetBrains Mono','Fira Code',Consolas,Menlo,'DejaVu Sans Mono',monospace"


def ventana(ancho: int, alto: int, titulo: str, cuerpo: str) -> str:
    """Ventana de terminal con efecto de monitor viejo (CRT): brillo, barrido y viñeta."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" font-family="{FUENTE}">
<defs>
<filter id="brillo" x="-5%" y="-5%" width="110%" height="110%">
<feGaussianBlur stdDeviation="1.4" result="halo"/>
<feMerge><feMergeNode in="halo"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>
<pattern id="barrido" width="4" height="3" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity="0.28"/></pattern>
<radialGradient id="vineta" cx="50%" cy="50%" r="75%"><stop offset="60%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity="0.55"/></radialGradient>
<clipPath id="pantalla"><rect x="1" y="41" width="{ancho - 2}" height="{alto - 42}" rx="11"/></clipPath>
</defs>
<rect x="0.5" y="0.5" width="{ancho - 1}" height="{alto - 1}" rx="12" fill="{FONDO}" stroke="{BORDE}"/>
<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/><circle cx="62" cy="20" r="6" fill="#28c840"/>
<text x="{ancho / 2}" y="25" fill="{TENUE}" font-size="13" text-anchor="middle">{escape(titulo)}</text>
<line x1="0" y1="40" x2="{ancho}" y2="40" stroke="{BORDE}"/>
<g clip-path="url(#pantalla)">
<g filter="url(#brillo)">
<animate attributeName="opacity" values="0;0.9;0.3;1" keyTimes="0;0.3;0.55;1" dur="0.6s" fill="freeze"/>
{cuerpo}
</g>
<rect x="0" y="40" width="{ancho}" height="{alto - 40}" fill="url(#barrido)"/>
<rect x="0" y="40" width="{ancho}" height="{alto - 40}" fill="url(#vineta)"/>
<rect x="0" y="40" width="{ancho}" height="{alto - 40}" fill="{VERDE}" fill-opacity="0">
<animate attributeName="fill-opacity" values="0;0.025;0;0.015;0" dur="5s" repeatCount="indefinite"/>
</rect>
</g>
</svg>"""


def aparece(inicio: float, ciclo: float, fin: float | None = None, repetir: bool = True) -> str:
    """Animación SMIL de opacidad en saltos (discrete): visible entre inicio y fin."""
    if not repetir:  # una sola vez y se queda visible
        return (
            f'<animate attributeName="opacity" values="0;1" keyTimes="0;{inicio / ciclo:.4f}" '
            f'dur="{ciclo}s" calcMode="discrete" fill="freeze"/>'
        )
    fin = fin if fin is not None else ciclo * 0.96
    tiempos = f"0;{inicio / ciclo:.4f};{fin / ciclo:.4f}"
    return (
        f'<animate attributeName="opacity" values="0;1;0" keyTimes="{tiempos}" '
        f'dur="{ciclo}s" calcMode="discrete" repeatCount="indefinite"/>'
    )
