---
applyTo: frontend/src/**/*.{ts,tsx}
---
# Frontend React/TypeScript Instructions

## Scope
- Applies to React and TypeScript source files under frontend/src/.

## Core Rules
- Preserve current UX behavior and existing backend API contracts.
- Follow existing patterns in App.tsx and ResearchWorkspace.tsx unless explicitly refactoring.
- Keep changes targeted; avoid broad visual or architectural rewrites unless requested.

## Data and Integration
- Treat backend API payloads as compatibility-sensitive.
- Keep SSE/log stream handling stable for real-time status updates.
- When changing API usage, align with backend route behavior in src/api/.

## Quality Bar
- Keep TypeScript and ESLint clean.
- Use existing styling/system conventions in the project.
- Prefer extracting small reusable components only when it clearly reduces complexity.

## Pre-merge Checks
- Run frontend lint and build checks when feasible:
  - npm run lint
  - npm run build
