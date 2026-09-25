"""Persistencia aislada del directorio personal real."""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

from arglyph import session
from arglyph.cli import main


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    return tmp_path


def test_clean_start_and_load(home):
    assert session.list_sessions() == []
    assert session.current_name() is None
    assert not (home / ".arglyph").exists()
    created = session.start("obsidian")
    data = json.loads((home / ".arglyph/sessions/obsidian.json").read_text())
    assert data == {
        "schema_version": 1, "name": "obsidian",
        "created_at": created.created_at,
        "commands": [], "evidence": [], "notes": [],
    }
    assert datetime.fromisoformat(created.created_at).utcoffset().total_seconds() == 0
    assert session.load("obsidian") == created
    assert session.current_name() == "obsidian"


def test_save_round_trip_and_independent_lists(home):
    first = session.Session("first")
    second = session.Session("second")
    first.notes.append("Descripción del laboratorio")
    session.save(first)
    assert session.load("first") == first
    assert second.notes == []
    first.notes.append("Segunda nota")
    session.save(first)
    assert session.load("first") == first
    assert len(list((home / ".arglyph/sessions").iterdir())) == 1


def test_duplicate_preserves_file_and_active_pointer(home):
    session.start("first")
    first = session.load("first")
    first.notes.append("Conservar")
    session.save(first)
    session.start("second")
    path = home / ".arglyph/sessions/first.json"
    original = path.read_bytes()
    with pytest.raises(session.SessionError, match="ya existe"):
        session.start("first")
    assert path.read_bytes() == original
    assert session.current_name() == "second"


def test_listing_and_cli(home, capsys):
    assert main(["session", "list"]) == 0
    assert "No hay sesiones" in capsys.readouterr().out
    assert main(["session", "start", "zeta"]) == 0
    assert main(["session", "start", "alpha"]) == 0
    capsys.readouterr()
    assert [item.name for item in session.list_sessions()] == ["alpha", "zeta"]
    assert main(["session", "list"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("* alpha ")
    assert lines[1].startswith("  zeta ")
    assert main(["session", "start", "alpha"]) == 1
    assert "ya existe" in capsys.readouterr().err


@pytest.mark.parametrize("name", ["", "../escape", "a/b", "a\\b", "C:foo",
                                      "CON", "con", "nul", "com1", "lpt9",
                                      "a.", "a b", "Mixed", "a" * 65])
def test_invalid_names_do_not_write(home, name):
    with pytest.raises(session.SessionError):
        session.start(name)
    with pytest.raises(session.SessionError):
        session.save(session.Session(name))
    with pytest.raises(session.SessionError):
        session.load(name)
    assert not (home / ".arglyph").exists()


@pytest.mark.parametrize("content", ["{broken", "[]", "{}",
    ('{"schema_version": 2, "name": "bad", "created_at": "2026-09-24", '
     '"commands": [], "evidence": [], "notes": []}')])
def test_corrupt_session_fails_cleanly(home, capsys, content):
    session.start("bad")
    (home / ".arglyph/sessions/bad.json").write_text(content, encoding="utf-8")
    with pytest.raises(session.SessionError):
        session.load("bad")
    assert main(["session", "list"]) == 1
    error = capsys.readouterr().err
    assert "invalida" in error
    assert "Traceback" not in error


def test_failed_save_preserves_existing_json(home, monkeypatch):
    created = session.start("lab")
    path = home / ".arglyph/sessions/lab.json"
    original = path.read_bytes()
    created.notes.append("Nuevo estado")

    def fail_replace(source, target):
        raise OSError("No se pudo reemplazar")

    monkeypatch.setattr(session.os, "replace", fail_replace)
    with pytest.raises(OSError):
        session.save(created)
    assert path.read_bytes() == original
    assert list(path.parent.iterdir()) == [path]


def test_cli_persists_between_processes(tmp_path):
    env = dict(os.environ, HOME=str(tmp_path), USERPROFILE=str(tmp_path))
    command = [sys.executable, "-m", "arglyph.cli", "session"]
    start = subprocess.run(command + ["start", "persistent"], env=env,
                           capture_output=True, text=True, check=False)
    assert start.returncode == 0, start.stderr
    listing = subprocess.run(command + ["list"], env=env,
                             capture_output=True, text=True, check=False)
    assert listing.returncode == 0, listing.stderr
    assert "* persistent " in listing.stdout
    assert (tmp_path / ".arglyph/sessions/persistent.json").is_file()
