---
globs: "*.py"
description: Python coding standards
---

# Python Rules

## Style
- Follow PEP 8. Use `ruff` for linting when available.
- Maximum line length: 88 characters (Black default).
- Use snake_case for functions and variables, PascalCase for classes.

## Type hints
- Add type hints to all function signatures (parameters and return types).
- Use `from __future__ import annotations` for modern syntax.
- For complex types, use `typing` module (Optional, Union, List, Dict).

## Docstrings
- Every public function and class must have a docstring.
- Use Google-style docstrings:
  ```python
  def calculate_yield(data: pd.DataFrame, threshold: float = 0.95) -> float:
      """Calculate production yield rate from process data.

      Args:
          data: DataFrame containing process measurements.
          threshold: Minimum acceptable yield rate.

      Returns:
          Yield rate as a float between 0 and 1.

      Raises:
          ValueError: If data contains no valid measurements.
      """
  ```

## Error handling
- Never use bare `except:`. Always catch specific exceptions.
- Use custom exception classes for domain-specific errors.
- Log errors with context (what was being attempted, with what input).

## Imports
- Sort imports: stdlib → third-party → local (use `isort` or `ruff`).
- No wildcard imports (`from module import *`).
- Prefer absolute imports over relative imports.

## FastAPI specific (when applicable)
- Use Pydantic models for request/response schemas.
- Add OpenAPI descriptions to all endpoints.
- Use dependency injection for database sessions.
- Return proper HTTP status codes (201 for creation, 404 for not found).

## Testing
- Use `pytest` as the test framework.
- Name test files `test_{module}.py`.
- Use fixtures for reusable test setup.
- Mock external services, never call real APIs in tests.
