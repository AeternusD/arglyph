"""
Carga la base de conocimiento (KB) de arglyph.

La KB son archivos YAML, uno por herramienta (nmap.yaml, ffuf.yaml, ...).
Cada archivo describe la herramienta y cada uno de sus flags. Esta es la
pieza central del proyecto: crece a medida que estudias y la comunidad
aporta flags nuevos. Es 100% determinista y offline: no hay IA en tiempo
de ejecucion, solo tu conocimiento curado.

Dos fuentes se combinan (la de usuario tiene prioridad):
  1. La KB que viene con el paquete:            arglyph/kb/*.yaml
  2. Una KB personal opcional del usuario:      $ARGLYPH_KB/*.yaml
     (o ~/.arglyph/kb/*.yaml si existe)

Asi cualquiera puede extender arglyph sin tocar el codigo del paquete.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml

# KB empaquetada: carpeta kb/ que vive junto a este archivo.
_PACKAGE_KB = Path(__file__).parent / "kb"


def _user_kb_dirs():
    """Devuelve las carpetas de KB personal del usuario, si existen."""
    dirs = []
    env = os.environ.get("ARGLYPH_KB")
    if env:
        dirs.append(Path(env).expanduser())
    default = Path.home() / ".arglyph" / "kb"
    if default.exists():
        dirs.append(default)
    return dirs


def _load_dir(directory: Path) -> dict:
    """Carga todos los .yaml de una carpeta en un dict {herramienta: datos}."""
    tools = {}
    if not directory.exists():
        return tools
    for path in sorted(directory.glob("*.yaml")):
        with open(path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        name = data.get("name") or path.stem
        tools[name] = data
    return tools


def load_kb() -> dict:
    """Devuelve la KB completa: {herramienta: {summary, url, flags:{...}}}.

    La KB de usuario sobreescribe/complementa a la del paquete por herramienta.
    """
    kb = _load_dir(_PACKAGE_KB)
    for user_dir in _user_kb_dirs():
        kb.update(_load_dir(user_dir))
    return kb


def known_tools(kb: dict | None = None):
    """Lista de herramientas que arglyph sabe explicar."""
    kb = kb if kb is not None else load_kb()
    return sorted(kb.keys())
