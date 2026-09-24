"""
Helper de color para terminal usando codigos ANSI puros.

No usamos una libreria externa (como rich) a proposito: mantener el runtime
con una sola dependencia (PyYAML) es parte de la filosofia de arglyph. La
herramienta debe funcionar offline, en cualquier Kali/box, sin sorpresas.
"""
import os
import sys

# Codigos ANSI. Se vacian si el color esta desactivado.
_CODES = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "gray": "\033[90m",
}


def supports_color(force: bool = False, disable: bool = False) -> bool:
    """Decide si emitimos color.

    - disable=True  -> nunca (respeta --no-color y la variable NO_COLOR).
    - force=True    -> siempre.
    - por defecto   -> solo si stdout es una terminal interactiva (TTY).
    """
    if disable or os.environ.get("NO_COLOR"):
        return False
    if force:
        return True
    return sys.stdout.isatty()


class Palette:
    """Envuelve texto en codigos ANSI (o no, si el color esta apagado)."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        if not self.enabled:
            return text
        return f"{_CODES[code]}{text}{_CODES['reset']}"

    def bold(self, t):    return self._wrap("bold", t)
    def dim(self, t):     return self._wrap("dim", t)
    def red(self, t):     return self._wrap("red", t)
    def green(self, t):   return self._wrap("green", t)
    def yellow(self, t):  return self._wrap("yellow", t)
    def blue(self, t):    return self._wrap("blue", t)
    def magenta(self, t): return self._wrap("magenta", t)
    def cyan(self, t):    return self._wrap("cyan", t)
    def gray(self, t):    return self._wrap("gray", t)
