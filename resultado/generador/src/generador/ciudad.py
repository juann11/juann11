"""Ciudad 3D isométrica: cada día es un edificio y su altura son las contribuciones."""

from generador.culebrita import _posiciones
from generador.tema import NIVELES, TENUE, VERDE, ventana

ANCHO, ALTO = 860, 410
# vectores de la proyección: avanzar una semana (columna) y un día (fila).
# las semanas van casi en horizontal para que se vea como un skyline y no como una franja diagonal
COL = (12.4, 2.2)
FILA = (-6.0, 5.6)
ALTO_MAX = 150
# shortcut: solo un edificio muy alto en la esquina de atrás a la izquierda se cortaría arriba; casi nunca pasa
Y0 = 190
# caras izquierda y derecha más oscuras que el techo, por nivel
CARA_IZQ = ["#0d1117", "#082e1b", "#004520", "#18702b", "#258c37"]
CARA_DER = ["#11161d", "#0b3a22", "#005728", "#1f8a36", "#2eb045"]
EASE = 'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"'


def _pts(puntos) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in puntos)


def _caras(x: float, y: float, alto: float) -> dict[str, list[tuple[float, float]]]:
    """Los 3 polígonos visibles de un edificio cuya base empieza en la esquina (x, y)."""
    a = (x, y)
    b = (x + COL[0], y + COL[1])
    c = (b[0] + FILA[0], b[1] + FILA[1])
    d = (x + FILA[0], y + FILA[1])

    def sube(p):
        return (p[0], p[1] - alto)

    return {
        "izq": [sube(d), sube(c), c, d],  # el frente, mirando hacia abajo
        "der": [sube(b), sube(c), c, b],  # el costado derecho
        "techo": [sube(a), sube(b), sube(c), sube(d)],
    }


def svg_ciudad(dias: list[dict]) -> str:
    posiciones = _posiciones(dias)
    maximo = max((d["cantidad"] for d in dias), default=0)
    columnas = max((c for c, _ in posiciones), default=0) + 1
    # centra el piso completo en el ancho: de la esquina más a la izquierda a la más a la derecha
    izquierda = 6 * FILA[0]
    derecha = columnas * COL[0]
    cx = ANCHO / 2 - (izquierda + derecha) / 2

    partes = [f'<text x="32" y="66" fill="{VERDE}" font-size="15">~$ ./ciudad.sh --3d</text>']
    # de atrás hacia adelante (fila, luego semana) para que lo cercano tape a lo lejano
    for (col, fila), d in sorted(zip(posiciones, dias), key=lambda p: (p[0][1], p[0][0])):
        x = cx + col * COL[0] + fila * FILA[0]
        y = Y0 + col * COL[1] + fila * FILA[1]
        nivel = d["nivel"]
        if not d["cantidad"]:
            partes.append(f'<polygon class="techo" points="{_pts(_caras(x, y, 0)["techo"])}" fill="{NIVELES[0]}"/>')
            continue
        alto = 6 + d["cantidad"] / maximo * ALTO_MAX
        plano, final = _caras(x, y, 0), _caras(x, y, alto)
        empieza = f"{0.3 + (col + fila) * 0.025:.2f}s"
        caras = []
        for nombre, color, clase in (
            ("izq", CARA_IZQ[nivel], ""),
            ("der", CARA_DER[nivel], ""),
            ("techo", NIVELES[nivel], ' class="techo"'),
        ):
            caras.append(
                f'<polygon{clase} points="{_pts(plano[nombre])}" fill="{color}">'
                f'<animate attributeName="points" values="{_pts(plano[nombre])};{_pts(final[nombre])}" '
                f'begin="{empieza}" dur="0.7s" fill="freeze" {EASE}/></polygon>'
            )
        partes.append(f'<g class="edificio">{"".join(caras)}</g>')

    if maximo:
        record = max(dias, key=lambda d: d["cantidad"])
        pie = f'{sum(d["cantidad"] for d in dias)} contribuciones · edificio más alto: {maximo} el {record["fecha"]}'
    else:
        pie = "todavía no hay edificios: a programar"
    partes.append(f'<text x="32" y="{ALTO - 20}" fill="{TENUE}" font-size="12">{pie}</text>')
    return ventana(ANCHO, ALTO, "juann11@github: ~/ciudad", "\n".join(partes))
