"""Modelo y persistencia de sesiones; no imprime ni ejecuta comandos."""
from __future__ import annotations

import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


class SessionError(ValueError):
    """Datos o nombre de sesion invalidos."""


@dataclass
class Session:
    name: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: int = 1
    commands: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    notes: list = field(default_factory=list)


def _root() -> Path:
    return Path.home() / ".arglyph"


def _validate_name(name: str) -> None:
    # Un mismo nombre representa el mismo archivo en Windows y Linux.
    reserved = {"con", "prn", "aux", "nul"}
    reserved.update(f"{prefix}{i}" for prefix in ("com", "lpt")
                    for i in range(1, 10))
    if (not isinstance(name, str)
            or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", name)
            or name in reserved):
        raise SessionError(
            "Nombre invalido: usa 1-64 letras minusculas ASCII, numeros, "
            "guiones o guiones bajos; empieza con letra o numero y evita "
            "nombres reservados de Windows (con, nul, com1, etc.).")


def _path(name: str) -> Path:
    _validate_name(name)
    return _root() / "sessions" / f"{name}.json"


def _validate(session: Session) -> None:
    _validate_name(session.name)
    if type(session.schema_version) is not int or session.schema_version != 1:
        raise SessionError("Version de esquema de sesion no compatible.")
    try:
        datetime.fromisoformat(session.created_at)
    except (TypeError, ValueError) as exc:
        raise SessionError("created_at debe ser una fecha ISO 8601.") from exc
    if not all(isinstance(value, list) for value in
               (session.commands, session.evidence, session.notes)):
        raise SessionError("commands, evidence y notes deben ser listas.")


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Cerrar el temporal antes de reemplazar tambien funciona en Windows.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent,
                delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def save(session: Session) -> None:
    """Guarda el estado completo reemplazando el archivo de forma atomica."""
    _validate(session)
    content = json.dumps(asdict(session), ensure_ascii=False, indent=2) + "\n"
    _atomic_write(_path(session.name), content)


def load(name: str) -> Session:
    """Carga y valida una sesion existente."""
    path = _path(name)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        required = {"schema_version", "name", "created_at", "commands",
                    "evidence", "notes"}
        if not isinstance(data, dict) or set(data) != required:
            raise SessionError("Campos de sesion invalidos.")
        session = Session(**data)
        _validate(session)
        if session.name != name:
            raise SessionError("El nombre no coincide con el archivo.")
        return session
    except (ValueError, TypeError, UnicodeError) as exc:
        raise SessionError(f"Sesion '{name}' invalida: {exc}") from exc


def start(name: str) -> Session:
    """Crea y activa una sesion; nunca sobrescribe una existente."""
    path = _path(name)
    session = Session(name=name)
    content = json.dumps(asdict(session), ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(content)
    except FileExistsError as exc:
        raise SessionError(f"La sesion '{name}' ya existe; usa otro nombre.") from exc
    _atomic_write(_root() / "current", name + "\n")
    return session


def list_sessions() -> list[Session]:
    """Devuelve las sesiones ordenadas por nombre, incluso en un inicio limpio."""
    return [load(path.stem) for path in
            sorted((_root() / "sessions").glob("*.json"))]


def current_name() -> str | None:
    """Lee el puntero activo; no tenerlo es un estado valido."""
    try:
        name = (_root() / "current").read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return None
    _validate_name(name)
    return name
