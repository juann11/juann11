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
    bloques = [r for r in raiz.iter(f"{NS}rect") if r.get("class") == "bloque"]
    assert len(bloques) == sum(1 for d in dias if d["nivel"])
    assert list(raiz.iter(f"{NS}animateMotion"))


def test_los_bloques_comidos_vuelven_cayendo_del_cielo():
    dias = _dias([i % 3 for i in range(60)])
    raiz = ET.fromstring(_svg(capa_culebrita(dias, 84)))
    for bloque in [r for r in raiz.iter(f"{NS}rect") if r.get("class") == "bloque"]:
        caida = bloque.find(f"{NS}animateTransform")
        assert caida is not None and caida.get("type") == "translate"
        alturas = [float(v.split()[1]) for v in caida.get("values").split(";")]
        assert min(alturas) < 0  # arranca arriba del calendario
        assert alturas[0] == alturas[-1] == 0  # el ciclo cierra en su puesto


def test_todos_los_tiempos_van_en_orden_y_dentro_del_ciclo():
    dias = _dias([i % 3 for i in range(60)])
    raiz = ET.fromstring(_svg(capa_culebrita(dias, 84)))
    for anim in raiz.iter():
        if anim.get("keyTimes"):
            tiempos = [float(t) for t in anim.get("keyTimes").split(";")]
            assert tiempos == sorted(tiempos) and tiempos[0] == 0 and tiempos[-1] <= 1
            lista = anim.get("keyPoints") or anim.get("values")
            assert len(tiempos) == len(lista.split(";"))
