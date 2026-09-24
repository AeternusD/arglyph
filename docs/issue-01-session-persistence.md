# Issue #1 — Persistencia de sesión (v0.2)

Primer y ÚNICO issue en marcha. No tocar parser de Nmap, report ni nada más
hasta cerrar este.

## Objetivo

Poder crear una sesión de laboratorio y que su estado sobreviva entre
invocaciones del CLI (cada comando es un proceso nuevo, así que el estado va
en disco).

Comandos a implementar:
- `arglyph session start <nombre>` — crea la sesión y la marca como activa.
- `arglyph session list` — lista las sesiones existentes y marca la activa.

## Diseño

- Modelo `Session` (dataclass) con, como mínimo:
  - `schema_version: 1`
  - `name`
  - `created_at` (ISO 8601)
  - `commands: []`  (se llenará en issues siguientes)
  - `evidence: []`  (se llenará en issues siguientes)
  - `notes: []`     (se llenará en issues siguientes)
- Persistencia: un JSON por sesión en `~/.arglyph/sessions/<nombre>.json`.
- Puntero de sesión activa: `~/.arglyph/current` (guarda el nombre).
- `load(nombre)` / `save(session)` en un módulo nuevo `arglyph/session.py`.
- El core devuelve/opera sobre objetos; el CLI se encarga de imprimir.

Ejemplo de archivo generado:

```json
{
  "schema_version": 1,
  "name": "obsidian",
  "created_at": "2026-09-23T18:00:00",
  "commands": [],
  "evidence": [],
  "notes": []
}
```

## Fuera de alcance (NO hacer en este issue)

- parser de Nmap / `ingest`
- `log`, `note`, `report`
- evidencia real (el array queda vacío por ahora)
- IDs de evidencia
- SQLite, IA, reglas, cualquier cosa de VISION.md

## Definición de hecho

- [ ] `session start` crea el JSON con `schema_version` y marca activa
- [ ] `session list` muestra las sesiones y señala la activa
- [ ] volver a `session start` con un nombre existente no corrompe el archivo
      (decidir: error claro o reactivar; documentarlo)
- [ ] tests: creación, carga, listado, y arranque en limpio (sin carpeta previa)
- [ ] instalación limpia funciona (`pip install -e .`)
- [ ] README menciona los comandos nuevos
- [ ] `python -m pytest` en verde
