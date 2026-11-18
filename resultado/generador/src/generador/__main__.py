"""uv run python -m generador [carpeta]  →  escribe terminal.svg y panel.svg"""

import sys
from pathlib import Path

from generador.ascii import svg_ascii
from generador.datos import obtener
from generador.panel import svg_panel

salida = Path(sys.argv[1] if len(sys.argv) > 1 else "../svg")
salida.mkdir(parents=True, exist_ok=True)
(salida / "terminal.svg").write_text(svg_ascii(), encoding="utf-8")
(salida / "panel.svg").write_text(svg_panel(obtener()), encoding="utf-8")
print(f"SVG listos en {salida.resolve()}")
