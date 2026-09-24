"""Tests del motor de diseccion. Ejecuta con: python -m pytest"""
from arglyph.explain import dissect
from arglyph.knowledge import load_kb

KB = load_kb()


def _kinds(result):
    return [s["kind"] for s in result["segments"]]


def test_binario_conocido():
    r = dissect("nmap -sV 10.10.10.5", KB)
    assert r["known"] is True
    assert r["tool"] == "nmap"


def test_binario_desconocido():
    r = dissect("herramienta-inventada -x", KB)
    assert r["known"] is False


def test_flag_con_valor_pegado():
    # -p- : el flag conocido es -p y el valor pegado es "-"
    r = dissect("nmap -p- 10.10.10.5", KB)
    flag = next(s for s in r["segments"] if s["text"] == "-p-")
    assert flag["kind"] == "flag"
    assert flag["value"] == "-"
    # Debe traer la nota especifica de "-" (todos los puertos)
    assert flag["value_note"] is not None


def test_flag_con_valor_separado():
    r = dissect("nmap --min-rate 1000 10.10.10.5", KB)
    flag = next(s for s in r["segments"] if s["text"] == "--min-rate")
    assert flag["value"] == "1000"


def test_flag_igual():
    r = dissect("nmap --min-rate=5000 10.10.10.5", KB)
    flag = next(s for s in r["segments"] if s["text"] == "--min-rate")
    assert flag["value"] == "5000"


def test_posicional_ip():
    r = dissect("nmap -sV 10.10.10.5", KB)
    pos = next(s for s in r["segments"] if s["text"] == "10.10.10.5")
    assert pos["kind"] == "positional"
    assert "IP" in pos["title"]


def test_flag_desconocido():
    r = dissect("nmap --flag-que-no-existe", KB)
    seg = next(s for s in r["segments"] if s["text"] == "--flag-que-no-existe")
    assert seg["kind"] == "unknown_flag"


def test_ffuf_marcador_fuzz():
    # FUZZ va dentro del valor de -u; el motor debe detectarlo y anotarlo.
    r = dissect("ffuf -w lista.txt -u http://sitio/FUZZ", KB)
    u = next(s for s in r["segments"] if s["text"] == "-u")
    assert "FUZZ" in u["value"]
    assert u["value_note"] is not None and "FUZZ" in u["value_note"]
