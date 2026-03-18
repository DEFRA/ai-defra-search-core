# AI Defra Search — Agent Reference

This is the single source of truth for all AI agents working in this codebase. Read this file before acting. All platform wrappers (CLAUDE.md, .cursor/rules/project.mdc, .github/copilot-instructions.md) point here.

## Project

A microservices AI search application built for Defra. See `ARCHITECTURE.md` for service structure, data flows, and technical boundaries.

## Rules

Rules govern how code is written. Apply every rule whose scope matches the current task.

| Rule                                          | Scope                                      |
|-----------------------------------------------|--------------------------------------------|
| `.agents/rules/ai-agnosticism.md`             | All AI platform config and top-level docs  |

## Skills

Skills describe repeatable workflows. Load the matching `SKILL.md` and follow its instructions exactly.

| Skill                                         | When to use                                                   |
|-----------------------------------------------|---------------------------------------------------------------|
| `.agents/skills/create-rule/SKILL.md`         | Create a new coding rules file in `.agents/rules/`            |
| `.agents/skills/create-skill/SKILL.md`        | Create a new skill file in `.agents/skills/`                  |
| `.agents/skills/review-docs/SKILL.md`         | Review all docs across core and service repos for misalignment |

## Service `.agents` directories

Each service repository cloned into `services/` maintains its own `.agents/` directory with service-specific rules and skills that extend (not replace) the root-level ones.

| Service directory                            | What to find there                                             |
|----------------------------------------------|----------------------------------------------------------------|
| `services/ai-defra-search-agent/.agents/`    | Rules and skills specific to the Agent service (Python/FastAPI)|
| `services/ai-defra-search-frontend/.agents/` | Rules and skills specific to the Frontend (Node.js/Hapi)      |
| `services/ai-defra-search-knowledge/.agents/`| Rules and skills specific to the Knowledge service            |

When working inside a service, load both the root-level rules and skills AND the service-specific ones. Service-level rules take precedence over root-level rules where they conflict.

## Adding new rules and skills

- Run the `create-rule` skill to add a rule.
- Run the `create-skill` skill to add a skill.
- Both skills will update this file's tables as their final step.

## Project setup

Start all local services:

```bash
docker compose up
```

Services are orchestrated from `compose.yml` with per-service overrides in `service-compose/`.