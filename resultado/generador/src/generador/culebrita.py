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

    # tiempos en segundos: la culebrita termina, se esconde y luego llueven los bloques tipo Tetris
    fin_culebra = (len(camino) - 1 + LARGO) * SEG_POR_PASO
    # columna por columna de izquierda a derecha, y en cada una de abajo hacia arriba (se apilan)
    orden_caida = sorted(comidos, key=lambda p: (p[0], -p[1]))
    entre_bloques = min(0.07, 1.8 / max(len(orden_caida), 1))
    empieza_caida = {p: fin_culebra + 0.4 + i * entre_bloques for i, p in enumerate(orden_caida)}
    CAE, REBOTA = 0.5, 0.16
    ultimo = max(empieza_caida.values(), default=fin_culebra)
    duracion = ultimo + CAE + 2 * REBOTA + 1.0
    dur = f'dur="{duracion:.2f}s" repeatCount="indefinite"'

    def k(segundos: float) -> str:
        return f"{segundos / duracion:.4f}"

    partes = [f'<g transform="translate({x0:.1f},{y0})">']
    # el calendario de fondo; los días comidos dejan su hueco oscuro
    for (col, fila), d in zip(posiciones, dias):
        color = NIVELES[0] if (col, fila) in comidos else NIVELES[d["nivel"]]
        partes.append(
            f'<rect class="dia" x="{col * PASO}" y="{fila * PASO}" width="{CELDA}" height="{CELDA}" rx="2" fill="{color}"/>'
        )

    # el bloque de cada día comido: desaparece cuando lo muerde la culebrita y vuelve cayendo del cielo
    nivel_de = {p: d["nivel"] for p, d in zip(posiciones, dias)}
    for (col, fila), t0 in empieza_caida.items():
        t_comido = comidos[(col, fila)] * SEG_POR_PASO
        arriba = (fila + 1) * PASO + 28  # arranca por encima del calendario
        tiempos = ";".join(
            ["0", k(t0 - 0.01), k(t0), k(t0 + CAE), k(t0 + CAE + REBOTA), k(t0 + CAE + 2 * REBOTA), "1"]
        )
        partes.append(
            f'<rect class="bloque" x="{col * PASO}" y="{fila * PASO}" width="{CELDA}" height="{CELDA}" rx="2" '
            f'fill="{NIVELES[nivel_de[(col, fila)]]}">'
            f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;{k(t_comido)};{k(t0)}" calcMode="discrete" {dur}/>'
            # gravedad: acelera al caer (ease-in), rebota 3 px y se queda quieto
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0;0 0;0 -{arriba};0 0;0 -3;0 0;0 0" keyTimes="{tiempos}" calcMode="spline" '
            f'keySplines="0 0 1 1;0 0 1 1;0.55 0 1 0.45;0.2 0.6 0.4 1;0.6 0 0.8 0.4;0 0 1 1" {dur}/></rect>'
        )

    # la culebrita: cada segmento hace el mismo camino, un paso detrás del anterior
    ruta = "M" + " L".join(f"{c * PASO} {f * PASO}" for c, f in camino)
    recorrido_seg = (len(camino) - 1) * SEG_POR_PASO
    for i in range(LARGO):
        arranca = i * SEG_POR_PASO
        termina = arranca + recorrido_seg
        opacidad = 1 - i / (LARGO + 1)
        partes.append(
            f'<rect width="{CELDA}" height="{CELDA}" rx="3" fill="#e6edf3" fill-opacity="{opacidad:.2f}">'
            f'<animateMotion path="{ruta}" {dur} calcMode="linear" '
            f'keyPoints="0;0;1;1" keyTimes="0;{k(arranca)};{k(termina)};1"/>'
            # al terminar de comer se esconde mientras llueven los bloques
            f'<animate attributeName="opacity" values="1;0" keyTimes="0;{k(fin_culebra + 0.1)}" calcMode="discrete" {dur}/>'
            f"</rect>"
        )
    partes.append("</g>")
    return partes
