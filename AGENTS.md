# Instrucciones para agentes — arglyph

Fuente de verdad del proyecto. Cualquier agente (Claude Code, Codex, Cursor…)
lee este archivo. Mantenerlo corto y operativo. La visión a largo plazo vive en
VISION.md; NO se implementa hoy.

## Hito actual: SOLO v0.2

Objetivo:
Registrar una sesión de laboratorio, ingerir la salida XML de Nmap, convertirla
en evidencia estructurada y exportar un reporte Markdown legible que combine
comandos + explicación + hallazgos.

Sin IA. Sin frontend. Sin grafos visuales. Sin base vectorial.

## Reglas de arquitectura

- La lógica de dominio (core) va SEPARADA del renderizado del CLI.
- Los parsers y el core DEVUELVEN datos estructurados; NO imprimen.
- Se REUTILIZA el parser de comandos existente `dissect()` (en `explain.py`);
  no se reescribe. El reporte lo usa para explicar cada comando registrado.
- Persistencia de sesión: un archivo JSON por sesión en
  `~/.arglyph/sessions/<nombre>.json`, con puntero a la sesión activa.
- Todo JSON de sesión lleva `schema_version: 1` desde el día uno.
- Los IDs de evidencia son secuenciales POR sesión: E01, E02, … (no globales).

## Alcance del parser de Nmap

Parsear SOLO (desde el XML `-oX`):
- host arriba (up)
- puertos TCP abiertos
- servicio
- product/version cuando exista

Cada evidencia guarda su `source_file`. Reingerir el MISMO archivo en la misma
sesión NO duplica evidencia (idempotente), salvo `--force`.

## Explícitamente FUERA DE ALCANCE en v0.2

- SQLite u otra BD
- LLMs / cualquier llamada a un modelo
- motor de reglas (evidencia → checks)
- TUI o interfaz web
- embeddings / RAG / base vectorial
- visualización de grafos
- ejecución autónoma de comandos
- del XML de Nmap: NSE scripts, OS fingerprinting, UDP, traceroute

Si crees que algo de esta lista "ayudaría", NO lo hagas. Va en otra versión.

## Quality gate (antes de dar por hecho un issue)

- suite de tests completa en verde (`python -m pytest`)
- XML malformado falla limpio (sin traceback feo)
- ingest duplicado no duplica evidencia
- instalación limpia funciona (`pip install -e .`)
- README actualizado si cambian comandos
- el reporte generado es legible sin editarlo a mano

## Estilo de trabajo

- Un solo issue por PR. PRs pequeños.
- No se abre el siguiente issue hasta que el anterior quede utilizable.
- Un solo agente modifica código a la vez; los demás solo revisan.
