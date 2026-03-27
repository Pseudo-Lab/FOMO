---
globs: "*"
description: Universal rules for all file types
---

# General Rules

## Git commit messages
Use conventional commits format:
- `feat: {description}` — new feature
- `fix: {description}` — bug fix
- `refactor: {description}` — code change that neither fixes nor adds
- `test: {description}` — adding or updating tests
- `docs: {description}` — documentation changes
- `chore: {description}` — maintenance tasks
- `style: {description}` — formatting, no logic change

Rules:
- Subject line max 72 characters.
- Use imperative mood: "add feature" not "added feature".
- No period at end of subject line.
- Body (if needed) explains WHY, not WHAT.

## File organization
- One concept per file. Don't mix unrelated logic.
- Group related files in directories.
- Keep directory nesting under 4 levels.
- Name files descriptively: `user-auth.ts` not `utils2.ts`.

## Comments
- Don't comment WHAT the code does — the code should be self-explanatory.
- Comment WHY when the reason isn't obvious.
- Remove commented-out code. Use git history instead.
- TODO format: `// TODO(username): description — issue #123`

## Security
- Never commit .env files. Add to .gitignore.
- Never log sensitive data (passwords, tokens, PII).
- Use parameterized queries for all database operations.
- Validate and sanitize all user input at the boundary.

## Documentation
- README.md at project root with setup instructions.
- Update docs when changing behavior.
- API changes must update the relevant documentation.
