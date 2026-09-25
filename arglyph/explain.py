"""
Nucleo de arglyph: diseccionar un comando en segmentos explicados.

El flujo es:
  1. shlex.split  -> partir la linea en tokens respetando comillas.
  2. El primer token es el binario -> lo buscamos en la KB.
  3. Cada token siguiente se clasifica:
       - flag conocido (con o sin valor)
       - flag desconocido (aun no esta en la KB)
       - valor posicional (IP, URL, wordlist, keyword FUZZ, etc.)
  4. Devolvemos una lista de "segmentos" estructurados.

Devolver segmentos estructurados (no texto ya formateado) es deliberado:
el mismo motor alimentara al generador de writeups (comando `report` en la
v0.2) reutilizando estos mismos datos. La CLI solo se encarga de pintarlos.
"""
import re
import shlex

# --- Heuristicas para clasificar valores posicionales -----------------------

_IPV4 = re.compile(r"^\d{1,3}(\.\d{1,3}){3}(/\d{1,2})?$")   # 10.10.10.5 o /24
_URL = re.compile(r"^https?://", re.IGNORECASE)
_DOMAIN = re.compile(r"^([a-z0-9-]+\.)+[a-z]{2,}$", re.IGNORECASE)


def _classify_positional(token: str) -> str:
    """Adivina que representa un token que no es un flag."""
    if token == "FUZZ" or "FUZZ" in token:
        return "Punto de fuzzing (marcador FUZZ)"
    if _IPV4.match(token):
        return "Objetivo (direccion IP o rango CIDR)"
    if _URL.match(token):
        return "Objetivo (URL)"
    if _DOMAIN.match(token):
        return "Objetivo (dominio)"
    if token.endswith((".txt", ".lst", ".list")):
        return "Ruta a un diccionario/wordlist"
    return "Valor posicional"


def _resolve_flag(token: str, flags: dict):
    """Resuelve un token de flag contra la KB de la herramienta.

    Maneja los tres estilos que aparecen en la practica:
      --min-rate=1000   -> se parte por '='
      -p-  /  -p80      -> el flag conocido es prefijo, el resto es el valor
      -sV               -> coincidencia exacta

    Devuelve (clave_flag, valor_pegado_o_None, info_dict_o_None).
    """
    # Estilo --flag=valor
    if token.startswith("--") and "=" in token:
        key, _, value = token.partition("=")
        if key in flags:
            return key, value, flags[key]

    # Coincidencia exacta (ej. -sV, -A, --min-rate sin valor pegado)
    if token in flags:
        return token, None, flags[token]

    # Valor pegado al flag corto (ej. -p-, -p80). Buscamos el flag conocido
    # mas largo que sea prefijo del token; lo que sobra es el valor.
    best = None
    for key in flags:
        if key.startswith("--"):
            continue  # el pegado sin '=' es cosa de flags cortos
        if (token.startswith(key) and len(token) > len(key)
                and (best is None or len(key) > len(best))):
            best = key
    if best is not None:
        value = token[len(best):]
        return best, value, flags[best]

    return None, None, None


def dissect(command: str, kb: dict) -> dict:
    """Disecciona `command` usando la KB. Devuelve un dict estructurado."""
    tokens = shlex.split(command)
    if not tokens:
        return {"tool": None, "known": False, "segments": [], "raw": command}

    tool_name = tokens[0]
    tool = kb.get(tool_name)
    segments = []

    if tool is None:
        # No conocemos el binario: lo reportamos pero seguimos, marcando
        # cada token como desconocido para que se vea que falta en la KB.
        segments.append({
            "kind": "tool",
            "text": tool_name,
            "title": "Herramienta no registrada en la KB",
            "what": f"'{tool_name}' aun no esta en tu base de conocimiento.",
            "why": None, "pro": None, "value": None,
        })
        return {"tool": tool_name, "known": False,
                "segments": segments, "raw": command}

    # Segmento del binario
    segments.append({
        "kind": "tool",
        "text": tool_name,
        "title": tool.get("summary", ""),
        "what": tool.get("description"),
        "why": None, "pro": None, "value": None,
        "url": tool.get("url"),
    })

    flags = tool.get("flags", {}) or {}
    i = 1
    while i < len(tokens):
        token = tokens[i]

        if token.startswith("-") and token != "-":
            key, glued_value, info = _resolve_flag(token, flags)

            if info is None:
                segments.append({
                    "kind": "unknown_flag",
                    "text": token,
                    "title": "Flag no registrado en la KB",
                    "what": "Este flag todavia no esta documentado. "
                            "Podrias agregarlo (ver CONTRIBUTING).",
                    "why": None, "pro": None, "value": None,
                })
                i += 1
                continue

            # El valor puede venir pegado (-p-) o como token siguiente
            # (--min-rate 1000), pero solo si el flag toma valor.
            value = glued_value
            if (value is None and info.get("takes_value")
                    and i + 1 < len(tokens) and not tokens[i + 1].startswith("-")):
                value = tokens[i + 1]
                i += 1

            # Nota especifica para ciertos valores (ej. -p- => todos los puertos)
            value_note = None
            if value is not None:
                value_note = (info.get("values", {}) or {}).get(value)
                # Si el valor lleva el marcador FUZZ, lo señalamos: ahi es
                # donde ffuf (u otro fuzzer) inyecta cada palabra del diccionario.
                if value_note is None and "FUZZ" in value:
                    value_note = "Contiene el marcador FUZZ: punto donde se inyecta cada palabra."

            # En el estilo --flag=valor mostramos solo la clave del flag,
            # como en el estilo separado (--flag valor). Con -p- dejamos el token.
            display = token
            if token.startswith("--") and "=" in token:
                display = key

            segments.append({
                "kind": "flag",
                "text": display,
                "title": info.get("title", ""),
                "what": info.get("what"),
                "why": info.get("why"),
                "pro": info.get("pro"),
                "value": value,
                "value_note": value_note,
            })
            i += 1
        else:
            segments.append({
                "kind": "positional",
                "text": token,
                "title": _classify_positional(token),
                "what": None, "why": None, "pro": None, "value": None,
            })
            i += 1

    return {"tool": tool_name, "known": True,
            "segments": segments, "raw": command}
