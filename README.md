# api-pilot

**api-pilot** is an AI-native API testing platform that automatically generates, executes, and validates API test suites from OpenAPI specs, Postman collections, or raw cURL commands. It combines a FastAPI backend, an async task engine, and an AI orchestration layer to reduce manual test-writing effort for QA engineers.

## Tech Stack

| Layer       | Technology                                      |
|-------------|-------------------------------------------------|
| Backend     | Python 3.12+, FastAPI, SQLAlchemy 2.x, Pydantic v2, arq |
| AI Layer    | Anthropic Claude API (claude-sonnet-4-6)        |
| Frontend    | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Database    | PostgreSQL 16 (async via asyncpg)               |
| Cache/Queue | Redis 7                                         |
| Infra       | Docker Compose (local), Helm (production)       |

## Repository Layout

```
api-pilot/
├── backend/    → FastAPI application (see backend/README.md)
├── frontend/   → React UI (see frontend/README.md)
├── infra/      → Docker Compose + future Helm charts
└── docs/       → Architecture and project documentation
```

- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)
- [Infrastructure README](infra/README.md)
- [Documentation Index](docs/README.md)

## Status

> **Sprint 0 — Foundation Setup**
> Repository skeleton created. No dependencies installed yet.
