import xml.etree.ElementTree as ET

from generador.ascii import svg_ascii

NS = "{http://www.w3.org/2000/svg}"


def _con_clase(raiz, etiqueta, clase):
    return [e for e in raiz.iter(f"{NS}{etiqueta}") if e.get("class") == clase]


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
