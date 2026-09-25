# arglyph

> Disecciona comandos ofensivos **símbolo por símbolo**, desde una base de
> conocimiento que curas tú.

`arglyph` toma un comando de pentesting y te explica cada pieza: el binario, qué
hace cada flag, qué implica cada valor y **por qué** lo usarías. No memoriza
comandos por ti: te enseña a leerlos.

```
$ arglyph explain "nmap -sV -p- 10.10.10.5 --min-rate 1000"

  nmap -sV -p- 10.10.10.5 --min-rate 1000

  nmap
    Network Mapper: escaner de red, puertos y servicios.
  -sV
    Deteccion de version de servicios
    Interroga cada servicio para saber que software y version corre.
    Por que: la version exacta es lo que te deja buscar CVEs concretos.
  -p-   (valor: -)
    Puertos a escanear
    valor: Los 65535 puertos TCP (escaneo completo).
  10.10.10.5
    Objetivo (direccion IP o rango CIDR)
  --min-rate   (valor: 1000)
    Tasa minima de paquetes por segundo
    Por que: acelera escaneos lentos a costa de mas ruido.
```

## Por qué existe

Cuando estás aprendiendo pentesting, el problema no es correr `nmap`: es
entender **qué** estás corriendo y **por qué**. Copiar un comando de un writeup
sin diseccionarlo no enseña nada.

`arglyph` convierte ese hábito de "explícame cada símbolo" en una herramienta:

- **Determinista y offline.** No usa IA en tiempo de ejecución. Es tu
  conocimiento curado en archivos YAML: fiable, rápido, sin depender de nada.
- **Dos niveles.** `--level principiante` (solo qué hace) para enseñar desde
  cero; `--level pro` (además el porqué y notas avanzadas) para ti.
- **Crece contigo.** Cada flag nuevo que estudias lo agregas a la base de
  conocimiento. Con el tiempo, el repo *es* tu manual personal — y el de quien
  lo use.

## Instalación

```bash
git clone https://github.com/tu-usuario/arglyph.git
cd arglyph
pip install -e .
```

Requiere Python 3.8+ y una sola dependencia (`PyYAML`).

## Uso

```bash
# Diseccionar un comando (nivel pro por defecto)
arglyph explain "ffuf -w users.txt -u http://sitio/login -X POST -fc 403"

# Nivel principiante (para enseñar, para tu village, para MAFER)
arglyph explain "nmap -sn 10.10.10.0/24" --level principiante

# Salida en JSON, para encadenar con otras herramientas
arglyph explain "nmap -sV 10.10.10.5" --json

# Ver qué herramientas conoce
arglyph tools
```

### Sesiones de laboratorio

```bash
arglyph session start obsidian
arglyph session list
```

`start` crea y activa una sesión; si el nombre ya existe, devuelve un error
sin modificar su contenido ni la sesión activa. `list` muestra las sesiones
ordenadas por nombre y marca la activa con `*`.

El estado se conserva entre invocaciones en
`~/.arglyph/sessions/<nombre>.json` y el nombre activo en `~/.arglyph/current`,
tanto en Windows como en Linux (`~` es la carpeta personal del usuario).
Cada JSON incluye `schema_version: 1`, fecha ISO 8601 en UTC y listas vacías
para comandos, evidencias y notas; su registro llegará en próximos issues.

Los nombres admiten de 1 a 64 letras minúsculas ASCII, números, guiones y
guiones bajos; deben empezar con letra o número. No se permiten nombres
reservados de Windows como `con`, `nul` o `com1`.

## La base de conocimiento (KB)

El corazón de `arglyph`. Cada herramienta es un YAML en `arglyph/kb/`:

```yaml
name: nmap
summary: "Network Mapper: escaner de red, puertos y servicios."
flags:
  "-sV":
    takes_value: false
    title: "Deteccion de version de servicios"
    what: "Interroga cada servicio para saber que software y version corre."
    why: "La version exacta es lo que te deja buscar CVEs concretos."
    pro: "Combinable con --version-intensity 0-9."
```

Puedes extenderla sin tocar el paquete, con una KB personal:

```bash
export ARGLYPH_KB=~/mis-notas/kb   # o crea ~/.arglyph/kb/
```

Los YAML de esa carpeta se combinan con los del paquete (los tuyos ganan).

Hoy trae: **nmap**, **ffuf**, **gobuster**, **hydra**. Los dos últimos son
stubs a propósito: buen punto de partida para tu primer aporte.

## Roadmap

- [x] **v0.1** — `explain`: disección de comandos desde la KB.
- [ ] **v0.2** — `log` + `report`: registrar los comandos de una sesión y
  generar un writeup en Markdown con cada comando ya explicado.
- [ ] **v0.3** — scoring CVSS y export a HTML.
- [ ] **v0.4** — modo "redacción para cliente" (ofusca IPs/datos sensibles al
  exportar un informe).
- [ ] **futuro** — reescritura del núcleo en Go para distribución en binario.

## Contribuir

Agregar una herramienta o un flag es agregar un YAML (o una entrada). Mira
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licencia

MIT.
