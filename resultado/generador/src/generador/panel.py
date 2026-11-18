"""Panel ~$ whoami: calendario de contribuciones, cifras y barras por mes."""

from datetime import date
from xml.sax.saxutils import escape

from generador.tema import BORDE, NIVELES, TENUE, TEXTO, VERDE, aparece, ventana

ANCHO, ALTO, CICLO = 860, 450, 4.0
MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _t(x, y, contenido, color=TEXTO, tamano=14, extra=""):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{tamano}"{extra}>{escape(str(contenido))}</text>'


def _calendario(dias: list[dict]) -> list[str]:
    celda, paso, y0 = 12, 15, 84
    # domingo = fila 0, igual que GitHub
    desfase = (date.fromisoformat(dias[0]["fecha"]).weekday() + 1) % 7 if dias else 0
    columnas: dict[int, list[str]] = {}
    for i, d in enumerate(dias):
        col, fila = divmod(i + desfase, 7)
        columnas.setdefault(col, []).append(
            f'<rect class="dia" x="{col * paso}" y="{y0 + fila * paso}" width="{celda}" height="{celda}" '
            f'rx="2" fill="{NIVELES[d["nivel"]]}"/>'
        )
    x0 = (ANCHO - len(columnas) * paso) / 2
    # cada semana aparece un poquito después de la anterior, de izquierda a derecha
    return [
        f'<g transform="translate({x0:.1f},0)" opacity="0">{aparece(0.1 + col * 0.015, CICLO, repetir=False)}{"".join(r)}</g>'
        for col, r in sorted(columnas.items())
    ]


def _cifras(datos: dict) -> list[str]:
    filas = [
        ("contribuciones", datos["total"], "racha actual", f'{datos["racha_actual"]} d'),
        ("mejor racha", f'{datos["mejor_racha"]} d', "repos públicos", datos["repos"]),
        ("estrellas", datos["estrellas"], "seguidores", datos["seguidores"]),
    ]
    partes = [_t(32, 262, "~$ whoami", VERDE, 15)]
    for i, (e1, v1, e2, v2) in enumerate(filas):
        y = 300 + i * 46
        t = 1.0 + i * 0.25
        for x, etiqueta, valor in ((32, e1, v1), (222, e2, v2)):
            partes.append(
                f'<g opacity="0">{aparece(t, CICLO, repetir=False)}'
                f'{_t(x, y, valor, VERDE, 24, " font-weight=\"700\"")}{_t(x, y + 18, etiqueta, TENUE, 12)}</g>'
            )
    lenguajes = " · ".join(nombre for nombre, _ in datos["lenguajes"]) or "-"
    partes.append(f'<g opacity="0">{aparece(1.9, CICLO, repetir=False)}{_t(32, 432, "lenguajes: " + lenguajes, TEXTO, 13)}</g>')
    return partes


def _barras(meses: list[tuple[str, int]]) -> list[str]:
    x0, base, alto_max, ancho_area = 460, 410, 120, 370
    partes = [_t(x0, 262, "~$ ./actividad.sh --meses", VERDE, 15)]
    partes.append(f'<line x1="{x0}" y1="{base}" x2="{x0 + ancho_area}" y2="{base}" stroke="{BORDE}"/>')
    maximo = max((n for _, n in meses), default=0) or 1
    paso = ancho_area / max(len(meses), 1)
    for i, (mes, n) in enumerate(meses):
        h = max(n / maximo * alto_max, 2)
        x = x0 + i * paso + paso * 0.2
        w = paso * 0.6
        inicio = f"{1.2 + i * 0.08:.2f}s"
        partes.append(
            f'<rect class="barra" x="{x:.1f}" y="{base}" width="{w:.1f}" height="0" rx="2" fill="{VERDE}">'
            f'<animate attributeName="height" from="0" to="{h:.1f}" begin="{inicio}" dur="0.6s" fill="freeze"/>'
            f'<animate attributeName="y" from="{base}" to="{base - h:.1f}" begin="{inicio}" dur="0.6s" fill="freeze"/>'
            f"</rect>"
        )
        partes.append(_t(f"{x + w / 2:.1f}", base + 16, MESES[int(mes[5:7]) - 1], TENUE, 11, ' text-anchor="middle"'))
        partes.append(_t(f"{x + w / 2:.1f}", f"{base - h - 6:.1f}", n, TENUE, 10, ' text-anchor="middle" opacity="0"').replace(
            "</text>", f"{aparece(1.9, CICLO, repetir=False)}</text>"
        ))
    return partes


def svg_panel(datos: dict) -> str:
    partes = [_t(32, 68, "~$ ./contributions.sh", VERDE, 15)]
    partes += _calendario(datos["dias"])
    partes.append(_t(32, 212, f'{datos["total"]} contribuciones en el último año', TENUE, 12))
    partes.append(f'<line x1="32" y1="230" x2="{ANCHO - 32}" y2="230" stroke="{BORDE}" stroke-dasharray="4 4"/>')
    partes += _cifras(datos)
    partes += _barras(datos["meses"])
    return ventana(ANCHO, ALTO, f'{datos["usuario"]}@github: ~/stats', "\n".join(partes))
