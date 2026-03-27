---
globs: "*.ts,*.tsx"
description: TypeScript and React coding standards
---

# TypeScript Rules

## Strict mode
- `strict: true` in tsconfig.json. No exceptions.
- Never use `any`. Use `unknown` if the type is truly unknown, 
  then narrow with type guards.
- Never use `@ts-ignore` or `@ts-expect-error` without a comment 
  explaining why and a linked issue to fix it.

## Naming
- camelCase for variables and functions.
- PascalCase for types, interfaces, classes, and React components.
- UPPER_SNAKE_CASE for constants.
- Prefix interfaces with descriptive names, not `I` (use `User` not `IUser`).

## Types
- Prefer `interface` for object shapes, `type` for unions and intersections.
- Export types that are used across files.
- Use discriminated unions for state management:
  ```typescript
  type RequestState =
    | { status: "idle" }
    | { status: "loading" }
    | { status: "success"; data: ResponseData }
    | { status: "error"; error: Error };
  ```

## React specific (when applicable)
- Use functional components only. No class components.
- Use named exports, not default exports.
- Keep components under 100 lines. Extract sub-components.
- Colocate styles, tests, and types with components.
- Use React hooks correctly:
  - Never call hooks conditionally.
  - Memoize expensive computations with `useMemo`.
  - Memoize callbacks with `useCallback` when passed as props.

## Next.js specific (when applicable)
- Use App Router conventions (app/ directory).
- Server components by default. Add "use client" only when needed.
- Use Server Actions for mutations.
- Handle loading and error states with loading.tsx and error.tsx.

## Error handling
- Always handle Promise rejections (try/catch or .catch()).
- Use Result pattern or discriminated unions for expected errors.
- Throw only for unexpected/programmer errors.

## Testing
- Use Vitest or Jest as the test framework.
- Name test files `{module}.test.ts` or `{module}.test.tsx`.
- Use React Testing Library for component tests (test behavior, not implementation).
- Mock API calls, never hit real endpoints in tests.
