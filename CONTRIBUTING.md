# Contribuir a arglyph

La forma más fácil (y más útil) de aportar es **ampliar la base de
conocimiento**: agregar herramientas o documentar flags que aún faltan.

## Agregar un flag a una herramienta existente

Abre el YAML correspondiente en `arglyph/kb/` (ej. `nmap.yaml`) y añade una
entrada bajo `flags:`:

```yaml
  "-Pn":
    takes_value: false          # true si el flag consume un valor (ej. -p 80)
    title: "Tratar todos los hosts como vivos"
    what: "Se salta el ping y escanea aunque el host no responda a ICMP."
    why: "Muchos firewalls bloquean ping; sin -Pn nmap los daria por caidos."
    pro: "Opcional: nota avanzada, se muestra solo en --level pro."
```

Campos:

| campo         | obligatorio | qué es                                             |
|---------------|-------------|----------------------------------------------------|
| `takes_value` | sí          | `true` si el flag lleva valor (`-p 80`, `-w x.txt`)|
| `title`       | sí          | nombre corto y claro de qué es el flag             |
| `what`        | sí          | qué hace, en una o dos frases                      |
| `why`         | no          | por qué lo usarías (se muestra en nivel pro)       |
| `pro`         | no          | nota avanzada (se muestra en nivel pro)            |
| `values`      | no          | notas para valores concretos (ver abajo)           |

### Notas para valores concretos

Si un valor específico merece explicación (ej. `-p-` = todos los puertos):

```yaml
  "-p":
    takes_value: true
    title: "Puertos a escanear"
    what: "Limita el escaneo a los puertos indicados."
    values:
      "-": "Los 65535 puertos TCP (escaneo completo)."
```

## Agregar una herramienta nueva

Crea `arglyph/kb/<herramienta>.yaml`:

```yaml
name: sqlmap
summary: "Automatiza deteccion y explotacion de inyeccion SQL."
description: "Descripcion de una o dos frases."
url: "https://github.com/sqlmapproject/sqlmap"
flags:
  "-u":
    takes_value: true
    title: "URL objetivo"
    what: "..."
    why: "..."
```

## Antes de enviar el PR

```bash
python -m pytest        # que los tests pasen
arglyph tools           # que tu herramienta aparezca
arglyph explain "sqlmap -u http://x/?id=1"   # que se vea bien
```

## Estilo

- Explicaciones en español, claras, sin asumir que el lector es experto.
- El `title` describe **qué es**; el `why` responde **por qué lo usarías**.
- Prioriza el criterio real sobre la definición del manual.
