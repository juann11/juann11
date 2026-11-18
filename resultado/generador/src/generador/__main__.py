"""uv run python -m generador [carpeta]  →  escribe terminal.svg, panel.svg y culebrita.svg"""

import sys
from pathlib import Path

from generador.ascii import svg_ascii
from generador.ciudad import svg_ciudad
from generador.culebrita import svg_culebrita
from generador.datos import obtener
from generador.panel import svg_panel

salida = Path(sys.argv[1] if len(sys.argv) > 1 else "../svg")
salida.mkdir(parents=True, exist_ok=True)
datos = obtener()
(salida / "terminal.svg").write_text(svg_ascii(), encoding="utf-8")
(salida / "panel.svg").write_text(svg_panel(datos), encoding="utf-8")
(salida / "culebrita.svg").write_text(svg_culebrita(datos["dias"]), encoding="utf-8")
(salida / "ciudad.svg").write_text(svg_ciudad(datos["dias"]), encoding="utf-8")
print(f"SVG listos en {salida.resolve()}")
