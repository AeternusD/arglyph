"""
Interfaz de linea de comandos de arglyph.

Subcomandos:
  explain "<comando>"   Disecciona un comando simbolo por simbolo.
  tools                 Lista las herramientas que arglyph sabe explicar.
  session start/list    Crea y lista sesiones persistentes.

(El subcomando `report`, que ensambla writeups a partir de una sesion, llega
en la v0.2 y reutilizara el motor de explain.py.)
"""
import argparse
import json
import sys

from . import __version__, session
from .colors import Palette, supports_color
from .explain import dissect
from .knowledge import known_tools, load_kb


def _print_segments(result: dict, level: str, pal: Palette):
    """Imprime la diseccion en la terminal, de forma legible."""
    raw = result["raw"]
    print()
    print("  " + pal.bold(raw))
    print()

    for seg in result["segments"]:
        kind = seg["kind"]

        # El texto del token, coloreado segun su tipo.
        if kind == "tool":
            head = pal.magenta(pal.bold(seg["text"]))
        elif kind == "flag":
            head = pal.cyan(seg["text"])
        elif kind == "unknown_flag":
            head = pal.red(seg["text"])
        else:  # positional
            head = pal.yellow(seg["text"])

        # Valor asociado (ej. --min-rate 1000)
        if seg.get("value") is not None:
            head += pal.gray(f"   (valor: {seg['value']})")

        print("  " + head)

        title = seg.get("title")
        if title:
            print("    " + pal.bold(title))

        what = seg.get("what")
        if what:
            print("    " + what)

        # Nota especifica del valor (ej. -p- => todos los puertos)
        vnote = seg.get("value_note")
        if vnote:
            print("    " + pal.gray("valor: ") + vnote)

        # En nivel principiante paramos aqui. En pro mostramos el 'por que'
        # y la nota avanzada, que es donde esta el criterio real.
        if level == "pro":
            why = seg.get("why")
            if why:
                print("    " + pal.green("Por que: ") + why)
            pro = seg.get("pro")
            if pro:
                print("    " + pal.blue("Nota pro: ") + pro)

        print()


def cmd_explain(args):
    kb = load_kb()
    pal = Palette(supports_color(disable=args.no_color))
    result = dissect(args.command, kb)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if not result["known"]:
        _print_segments(result, args.level, pal)
        print("  " + pal.yellow(
            f"'{result['tool']}' no esta en la KB todavia. "
            "Herramientas disponibles: " + ", ".join(known_tools(kb))))
        return 1

    _print_segments(result, args.level, pal)
    return 0


def cmd_tools(args):
    kb = load_kb()
    pal = Palette(supports_color(disable=args.no_color))
    print(pal.bold("Herramientas en la base de conocimiento:"))
    for tool in known_tools(kb):
        n = len(kb[tool].get("flags") or {})
        print(f"  {pal.magenta(tool):<20} {pal.gray(str(n) + ' flags documentados')}")
    return 0


def cmd_session(args):
    try:
        if args.session_cmd == "start":
            created = session.start(args.name)
            print(f"Sesion '{created.name}' creada y activa.")
        else:
            sessions = session.list_sessions()
            active = session.current_name()
            if not sessions:
                print("No hay sesiones.")
            for item in sessions:
                marker = "*" if item.name == active else " "
                print(f"{marker} {item.name}  {item.created_at}")
        return 0
    except (session.SessionError, OSError, UnicodeError) as exc:
        print(f"Error de sesion: {exc}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arglyph",
        description="Disecciona comandos ofensivos simbolo por simbolo, "
                    "desde una base de conocimiento que curas tu.",
    )
    parser.add_argument("--version", action="version",
                        version=f"arglyph {__version__}")

    # Opciones comunes a todos los subcomandos (asi --no-color funciona
    # tanto antes como despues del subcomando).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--no-color", action="store_true",
                        help="Desactiva el color en la salida.")

    sub = parser.add_subparsers(dest="cmd", required=True)

    p_explain = sub.add_parser(
        "explain", parents=[common], help="Disecciona un comando.")
    p_explain.add_argument(
        "command", help="El comando completo, entre comillas.")
    p_explain.add_argument(
        "--level", choices=["principiante", "pro"], default="pro",
        help="principiante = solo que hace; pro = ademas el por que (default).")
    p_explain.add_argument(
        "--json", action="store_true",
        help="Salida estructurada en JSON (para automatizar/encadenar).")
    p_explain.set_defaults(func=cmd_explain)

    p_tools = sub.add_parser(
        "tools", parents=[common], help="Lista las herramientas conocidas.")
    p_tools.set_defaults(func=cmd_tools)

    p_session = sub.add_parser(
        "session", parents=[common], help="Gestiona sesiones persistentes.")
    session_sub = p_session.add_subparsers(dest="session_cmd", required=True)
    p_start = session_sub.add_parser("start", help="Crea y activa una sesion.")
    p_start.add_argument("name", help="Nombre de la nueva sesion.")
    session_sub.add_parser("list", help="Lista sesiones; * marca la activa.")
    p_session.set_defaults(func=cmd_session)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        # Pasa al canalizar a head/less y cerrar antes de tiempo. Es normal:
        # salimos en silencio en vez de volcar un traceback feo.
        return 0


if __name__ == "__main__":
    sys.exit(main())
