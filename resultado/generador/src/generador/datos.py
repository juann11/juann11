"""Lee los datos públicos del perfil de GitHub (sin token obligatorio)."""

import json
import os
import re
import urllib.request
from collections import Counter

USUARIO = "juann11"

_CELDA = re.compile(r'<td[^>]*data-date="([\d-]+)"[^>]*id="([^"]+)"[^>]*data-level="(\d)"')
_TOOLTIP = re.compile(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(\d+) contribution')


def parsear_contribuciones(html: str) -> list[dict]:
    """Saca cada día del calendario: fecha, cantidad y nivel (0-4) de color."""
    cantidades = {celda: int(n) for celda, n in _TOOLTIP.findall(html)}
    dias = [
        {"fecha": fecha, "cantidad": cantidades.get(celda, 0), "nivel": int(nivel)}
        for fecha, celda, nivel in _CELDA.findall(html)
    ]
    return sorted(dias, key=lambda d: d["fecha"])


def rachas(dias: list[dict]) -> tuple[int, int]:
    """Devuelve (racha actual, mejor racha) en días seguidos con contribuciones."""
    mejor = seguidos = 0
    for d in dias:
        seguidos = seguidos + 1 if d["cantidad"] else 0
        mejor = max(mejor, seguidos)
    # si hoy va en 0, la racha de ayer sigue viva
    previos = dias[:-1] if dias and not dias[-1]["cantidad"] else dias
    actual = 0
    for d in reversed(previos):
        if not d["cantidad"]:
            break
        actual += 1
    return actual, mejor


def total_por_mes(dias: list[dict]) -> list[tuple[str, int]]:
    """Suma por mes (AAAA-MM) de los últimos 12 meses, en orden."""
    meses = Counter()
    for d in dias:
        meses[d["fecha"][:7]] += d["cantidad"]
    return sorted(meses.items())[-12:]


def _get(url: str) -> bytes:
    cabeceras = {"User-Agent": "perfil-generador"}
    if token := os.environ.get("GITHUB_TOKEN"):  # en el Action sube el límite de la API
        cabeceras["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=cabeceras), timeout=30) as r:
        return r.read()


def obtener(usuario: str = USUARIO) -> dict:
    """Junta todo lo que pintan los SVG."""
    html = _get(f"https://github.com/users/{usuario}/contributions").decode("utf-8")
    dias = parsear_contribuciones(html)
    perfil = json.loads(_get(f"https://api.github.com/users/{usuario}"))
    repos = json.loads(_get(f"https://api.github.com/users/{usuario}/repos?per_page=100"))
    propios = [r for r in repos if not r["fork"]]
    lenguajes = Counter(r["language"] for r in propios if r["language"])
    actual, mejor = rachas(dias)
    return {
        "usuario": usuario,
        "dias": dias,
        "total": sum(d["cantidad"] for d in dias),
        "racha_actual": actual,
        "mejor_racha": mejor,
        "repos": perfil["public_repos"],
        "estrellas": sum(r["stargazers_count"] for r in propios),
        "seguidores": perfil["followers"],
        "lenguajes": lenguajes.most_common(4),
        "meses": total_por_mes(dias),
    }
