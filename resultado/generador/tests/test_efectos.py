import xml.etree.ElementTree as ET
from datetime import date, timedelta

from generador.ascii import svg_ascii
from generador.ciudad import svg_ciudad

NS = "{http://www.w3.org/2000/svg}"


def _dias(cantidades):
    inicio = date(2025, 11, 16)  # domingo
    return [
        {"fecha": (inicio + timedelta(i)).isoformat(), "cantidad": c, "nivel": min(c, 4)}
        for i, c in enumerate(cantidades)
    ]


def _con_clase(raiz, etiqueta, clase):
    return [e for e in raiz.iter(f"{NS}{etiqueta}") if e.get("class") == clase]


# --- ciudad 3D ---

def test_ciudad_un_techo_por_dia_y_un_edificio_por_dia_activo():
    dias = _dias([i % 4 for i in range(70)])
    raiz = ET.fromstring(svg_ciudad(dias))
    assert len(_con_clase(raiz, "polygon", "techo")) == 70
    assert len(_con_clase(raiz, "g", "edificio")) == sum(1 for d in dias if d["cantidad"])


def test_los_edificios_crecen_desde_el_piso():
    raiz = ET.fromstring(svg_ciudad(_dias([0, 5, 1])))
    for edificio in _con_clase(raiz, "g", "edificio"):
        for cara in edificio.iter(f"{NS}polygon"):
            crece = cara.find(f"{NS}animate")
            assert crece is not None and crece.get("attributeName") == "points"
            plano, alto = crece.get("values").split(";")
            assert len(plano.split()) == len(alto.split())  # SMIL exige los mismos puntos


def test_el_mas_alto_es_el_dia_con_mas_contribuciones():
    raiz = ET.fromstring(svg_ciudad(_dias([1, 9, 2])))
    texto = " ".join(raiz.itertext())
    assert "9" in texto and "2025-11-17" in texto


def test_ciudad_sin_contribuciones_no_revienta():
    ET.fromstring(svg_ciudad(_dias([0] * 10)))


# --- CRT (va en el marco de todas las ventanas) ---

def test_ventanas_con_brillo_y_lineas_de_barrido():
    raiz = ET.fromstring(svg_ascii())
    assert raiz.find(f".//{NS}filter[@id='brillo']") is not None
    assert raiz.find(f".//{NS}pattern[@id='barrido']") is not None


# --- lluvia Matrix ---

def test_terminal_con_lluvia_animada_detras_del_nombre():
    raiz = ET.fromstring(svg_ascii())
    gotas = _con_clase(raiz, "text", "lluvia")
    assert len(gotas) >= 20
    assert all(g.find(f"{NS}animateTransform") is not None for g in gotas)
    # la lluvia se pinta antes (debajo) que el nombre
    orden = [e.get("class") for e in raiz.iter(f"{NS}text")]
    assert orden.index("lluvia") < orden.index("arte")
