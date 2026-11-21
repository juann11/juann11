import xml.etree.ElementTree as ET

from generador.culebrita import capa_culebrita, recorrido

NS = "{http://www.w3.org/2000/svg}"


def _dias(niveles):
    # 2025-11-16 es domingo: el día 0 cae en la fila 0
    from datetime import date, timedelta

    inicio = date(2025, 11, 16)
    return [
        {"fecha": (inicio + timedelta(i)).isoformat(), "cantidad": n, "nivel": n} for i, n in enumerate(niveles)
    ]


def test_recorrido_avanza_de_a_un_cuadro_y_pasa_por_todo_lo_activo():
    niveles = [0] * 30
    for i in (3, 10, 25):
        niveles[i] = 2
    camino, comidos = recorrido(_dias(niveles))
    assert camino[0] == (0, 0)
    for (c1, f1), (c2, f2) in zip(camino, camino[1:]):
        assert abs(c1 - c2) + abs(f1 - f2) == 1
    assert set(comidos) == {(0, 3), (1, 3), (3, 4)}  # (columna, fila) de los días 3, 10 y 25


def test_sin_contribuciones_no_revienta():
    camino, comidos = recorrido(_dias([0] * 14))
    assert camino == [(0, 0)] and comidos == {}
    ET.fromstring(_svg(capa_culebrita(_dias([0] * 14), 84)))


def _svg(partes):
    return f'<svg xmlns="http://www.w3.org/2000/svg">{"".join(partes)}</svg>'


def test_capa_valida_con_un_cuadro_por_dia_y_solo_se_comen_los_activos():
    dias = _dias([i % 3 for i in range(60)])
    raiz = ET.fromstring(_svg(capa_culebrita(dias, 84)))
    cuadros = [r for r in raiz.iter(f"{NS}rect") if r.get("class") == "dia"]
    assert len(cuadros) == 60
    comidos = [r for r in cuadros if r.find(f"{NS}animate") is not None]
    assert len(comidos) == sum(1 for d in dias if d["nivel"])
    assert list(raiz.iter(f"{NS}animateMotion"))
