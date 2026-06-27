# MEMORY.md — UnrealClaudeMCP · Índice maestro

> Punto de entrada de la memoria del proyecto. **Lee esto primero.**
> REGLA DURA — anti-huérfano: todo doc nuevo (plan, destripe, reference, decisión, ADR)
> se **ENLAZA aquí** al crearlo, o la próxima sesión no lo descubre.

## 📍 Estado de un vistazo

**Fecha:** 2026-05-29
**Milestone activo:** TBD · rama `fix/skill-console-vars` (sin PR abierto)
| Nombre | Tipo | Schedule | Acciones que toma | Estado | Block override |
|---|---|---|---|---|---|
| scripts/babysit_cascade.py | script (cron/launchd manual) | tras cooldown 24h post-merge | push PR2/PR3 a `NAFEMWEHBE/unreal-ai-connection` + Discord notify | local-only (gitignorado) | touch `.babysit-stop` |
| .github/workflows/tests.yml | GH Actions | on push/PR | pytest CI | ACTIVE | workflow_dispatch / disable |

## 🗂️ Mapa de memoria

| Capa | Fichero | Rol |
|---|---|---|
| Semántica estable | [PROJECT.md](PROJECT.md) | qué es, arquitectura, decisiones de fondo |
| Estado vivo | [STATUS.md](STATUS.md) | estado actual narrativo + automations live |
| Bitácora episódica | [MEMORY-SESIONES.md](MEMORY-SESIONES.md) | histórico append-only de todas las sesiones |
| Buffer corto | CONTEXTO-SESION-*.md | estado de la última sesión (rotable, máx 3) |
| Reglas proyecto | [CLAUDE.md](CLAUDE.md) | reglas específicas (las globales viven en ~/.claude) |

> Separación por **función**, no por antigüedad: lo estable (PROJECT) ≠ lo vivo (STATUS)
> ≠ el histórico (MEMORY-SESIONES) ≠ el buffer (CONTEXTO). Cada cosa a su sitio.

## 📄 Otros documentos

- [AGENTS.md](AGENTS.md) — _añadir 1 línea de qué es_
- [CHANGELOG.md](CHANGELOG.md) — _añadir 1 línea de qué es_
- [CONTRIBUTING.md](CONTRIBUTING.md) — _añadir 1 línea de qué es_
- [SECURITY.md](SECURITY.md) — _añadir 1 línea de qué es_
- [llms-install.md](llms-install.md) — _añadir 1 línea de qué es_
