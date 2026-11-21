"""Culebrita que recorre el calendario y se come los días con contribuciones."""

from datetime import date

from generador.tema import NIVELES

ANCHO = 860
CELDA, PASO = 12, 15
SEG_POR_PASO, LARGO = 0.07, 6


def _posiciones(dias: list[dict]) -> list[tuple[int, int]]:
    """(columna, fila) de cada día, con domingo en la fila 0 como GitHub."""
    desfase = (date.fromisoformat(dias[0]["fecha"]).weekday() + 1) % 7 if dias else 0
    return [divmod(i + desfase, 7) for i in range(len(dias))]


def recorrido(dias: list[dict]) -> tuple[list[tuple[int, int]], dict[tuple[int, int], int]]:
    """Camino cuadro a cuadro hacia el día activo más cercano, hasta comérselos todos.

    Devuelve el camino y, para cada cuadro comido, el paso en que la cabeza llega.
    """
    activos = {p for p, d in zip(_posiciones(dias), dias) if d["nivel"]}
    actual = (0, 0)
    camino, comidos = [actual], {}
    while activos:
        objetivo = min(activos, key=lambda p: (abs(p[0] - actual[0]) + abs(p[1] - actual[1]), p))
        while actual != objetivo:
            col, fila = actual
            if col != objetivo[0]:  # primero en horizontal, luego en vertical
                col += 1 if objetivo[0] > col else -1
            else:
                fila += 1 if objetivo[1] > fila else -1
            actual = (col, fila)
            camino.append(actual)
            if actual in activos:  # lo que encuentre de paso también se lo come
                activos.discard(actual)
                comidos[actual] = len(camino) - 1
    return camino, comidos


def capa_culebrita(dias: list[dict], y0: float) -> list[str]:
    """Calendario centrado en el ancho, con la culebrita comiéndoselo. Arranca en la altura y0."""
    posiciones = _posiciones(dias)
    camino, comidos = recorrido(dias)
    columnas = max((c for c, _ in posiciones), default=0) + 1
    x0 = (ANCHO - columnas * PASO) / 2
    duracion = (len(camino) + LARGO) * SEG_POR_PASO + 1.5
    partes = [f'<g transform="translate({x0:.1f},{y0})">']

    # el calendario: cada día comido se apaga cuando llega la cabeza y revive al final del ciclo
    for (col, fila), d in zip(posiciones, dias):
        color = NIVELES[d["nivel"]]
        anim = ""
        if (col, fila) in comidos:
            t = comidos[(col, fila)] * SEG_POR_PASO / duracion
            anim = (
                f'<animate attributeName="fill" values="{color};{NIVELES[0]};{color}" '
                f'keyTimes="0;{t:.4f};0.97" dur="{duracion:.2f}s" calcMode="discrete" repeatCount="indefinite"/>'
            )
        partes.append(
            f'<rect class="dia" x="{col * PASO}" y="{fila * PASO}" width="{CELDA}" height="{CELDA}" '
            f'rx="2" fill="{color}">{anim}</rect>'
        )

    # la culebrita: cada segmento hace el mismo camino, un paso detrás del anterior
    ruta = "M" + " L".join(f"{c * PASO} {f * PASO}" for c, f in camino)
    recorrido_seg = (len(camino) - 1) * SEG_POR_PASO
    for k in range(LARGO):
        arranca = k * SEG_POR_PASO / duracion
        termina = (k * SEG_POR_PASO + recorrido_seg) / duracion
        opacidad = 1 - k / (LARGO + 1)
        partes.append(
            f'<rect width="{CELDA}" height="{CELDA}" rx="3" fill="#e6edf3" fill-opacity="{opacidad:.2f}">'
            f'<animateMotion path="{ruta}" dur="{duracion:.2f}s" repeatCount="indefinite" calcMode="linear" '
            f'keyPoints="0;0;1;1" keyTimes="0;{arranca:.4f};{termina:.4f};1"/></rect>'
        )
    partes.append("</g>")
    return partes
