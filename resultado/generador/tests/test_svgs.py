import xml.etree.ElementTree as ET

from generador.ascii import KUVEX, svg_ascii
from generador.panel import svg_panel

NS = "{http://www.w3.org/2000/svg}"


def test_ascii_es_svg_valido_con_todas_las_lineas():
    svg = svg_ascii()
    raiz = ET.fromstring(svg)
    textos = ["".join(t.itertext()) for t in raiz.iter(f"{NS}text")]
    for linea in KUVEX:
        assert linea in textos


def test_ascii_esta_animado_y_con_ancho_fijo():
    raiz = ET.fromstring(svg_ascii())
    assert list(raiz.iter(f"{NS}animate"))
    # textLength obliga a que el bloque mida igual con cualquier fuente monoespaciada
    lineas = [t for t in raiz.iter(f"{NS}text") if "".join(t.itertext()) in KUVEX]
    assert all(t.get("textLength") for t in lineas)


def test_lineas_kuvex_del_mismo_ancho():
    assert len({len(l) for l in KUVEX}) == 1


def _datos():
    dias = [{"fecha": f"2026-01-{i % 28 + 1:02d}", "cantidad": i % 5, "nivel": i % 5} for i in range(371)]
    return {
        "usuario": "juann11",
        "dias": dias,
        "total": 217,
        "racha_actual": 3,
        "mejor_racha": 12,
        "repos": 7,
        "estrellas": 2,
        "seguidores": 4,
        "lenguajes": [("TypeScript", 2), ("C<>&", 1)],
        "meses": [("2025-12", 10), ("2026-01", 0), ("2026-02", 40)],
    }


def test_panel_es_svg_valido_y_escapa_texto():
    svg = svg_panel(_datos())
    ET.fromstring(svg)  # revienta si algo quedó sin escapar
    assert "C&lt;&gt;&amp;" in svg


def test_panel_muestra_las_cifras():
    texto = " ".join(ET.fromstring(svg_panel(_datos())).itertext())
    for cifra in ["217", "12", "7", "TypeScript"]:
        assert cifra in texto


def test_panel_pinta_un_cuadro_por_dia_y_una_barra_por_mes():
    raiz = ET.fromstring(svg_panel(_datos()))
    rects = list(raiz.iter(f"{NS}rect"))
    assert len([r for r in rects if r.get("class") == "dia"]) == 371
    assert len([r for r in rects if r.get("class") == "barra"]) == 3
