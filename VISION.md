# VISION — a dónde va arglyph (NO se construye hoy)

Este documento existe para que cualquier persona (o agente) entienda la
ambición del proyecto SIN confundirla con lo que toca implementar ahora.
Lo que se construye ahora está en AGENTS.md. Nada de aquí entra en el hito
actual.

## La idea de producto

arglyph aspira a ser un asistente de investigación para laboratorios de
ciberseguridad autorizados (HTB, PortSwigger, TryHackMe, CTFs, labs propios):
no "hackea por ti", sino que captura cómo investigas, organiza evidencia e
hipótesis, y convierte todo eso en conocimiento reutilizable.

El nombre de trabajo de esa visión completa es "Cyber Lab Copilot".
arglyph es la implementación incremental que se va acercando a ella.

## Arquitectura objetivo: tres capas

1. Facts — deterministas. Parsers convierten salidas de herramientas en
   evidencia (TCP/80 abierto, 403 en /admin). Sin IA.
2. Rules — conocimiento explícito. evidencia → checks sugeridos. Determinista.
3. Reasoning — OPCIONAL y encima de todo. Un LLM ayuda a razonar sobre los
   hechos, nunca es la fuente de verdad. Cada salida se ancla a evidencia
   (Evidence Graph) y se registra.

El LLM va ENCIMA de los hechos, no debajo.

## Piezas aparcadas (orden aproximado, no comprometido)

- evidencia → checks sugeridos deterministas (motor de reglas)
- Evidence Graph con IDs estables entre sesiones y relaciones E→S
- LLM en modo tutor (pistas socráticas), con feedback cualitativo del usuario
  (Útil / Muy vaga / Muy reveladora / Incorrecta) — leído a mano, sin KPIs
- hipótesis generadas por IA, marcadas y ancladas a evidencia
- Verified Knowledge: patrones aprobados manualmente
- similitud entre labs: empezar con Jaccard sobre tags, NO embeddings
- embeddings / RAG / base vectorial: solo si el uso real lo pide
- Replay Mode: convertir labs terminados en experiencias guiadas
- perfil de aprendizaje del usuario
- TUI o interfaz web (React/React Flow) para el grafo
- más parsers de herramientas (ffuf, gobuster, nikto, nuclei…)

## Principio de gobierno

"Diseñamos suficiente arquitectura para no encerrarnos, pero implementamos
únicamente lo que necesitamos en el siguiente laboratorio."

Cada hito debe terminar: funcionando, documentado, con tests, usable y
commiteado. Nunca varias mitades a medio hacer.
