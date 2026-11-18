from pathlib import Path

from generador.datos import parsear_contribuciones, rachas, total_por_mes

HTML = (Path(__file__).parent / "fixtures" / "contribuciones.html").read_text(encoding="utf-8")


def test_parsea_todos_los_dias_ordenados():
    dias = parsear_contribuciones(HTML)
    assert len(dias) >= 365
    fechas = [d["fecha"] for d in dias]
    assert fechas == sorted(fechas)


def test_la_suma_coincide_con_el_total_de_github():
    dias = parsear_contribuciones(HTML)
    assert sum(d["cantidad"] for d in dias) == 217


def test_nivel_entre_0_y_4():
    assert {d["nivel"] for d in parsear_contribuciones(HTML)} <= {0, 1, 2, 3, 4}


def _dias(cantidades):
    return [{"fecha": f"2026-01-{i + 1:02d}", "cantidad": c, "nivel": 0} for i, c in enumerate(cantidades)]


def test_rachas_actual_y_mejor():
    assert rachas(_dias([1, 1, 1, 0, 2, 2])) == (2, 3)


def test_racha_actual_no_se_rompe_si_hoy_aun_no_hay_commits():
    # el último día es hoy: si va en 0 todavía no cuenta como racha rota
    assert rachas(_dias([1, 1, 0])) == (2, 2)


def test_racha_en_cero():
    assert rachas(_dias([0, 0])) == (0, 0)


def test_total_por_mes_ultimos_12():
    dias = [
        {"fecha": "2025-12-31", "cantidad": 4, "nivel": 1},
        {"fecha": "2026-01-01", "cantidad": 2, "nivel": 1},
        {"fecha": "2026-01-15", "cantidad": 3, "nivel": 1},
    ]
    meses = total_por_mes(dias)
    assert meses[-2:] == [("2025-12", 4), ("2026-01", 5)]
    assert len(meses) <= 12
