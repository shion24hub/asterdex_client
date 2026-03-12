# Repository Guidelines
## Project Overview
<placeholder>

## Project Structure & Module Organization
<placeholder>

## Build, Test, and Development Commands
- `uv sync --dev`: install project + dev tooling into the local environment.
- `uv build`: build source and wheel distributions via `uv_build`.

If you add tests, prefer running them with `uv run pytest`.

## Coding Style & Naming Conventions
- Target Python `3.12+` (`.python-version` is `3.12`).
- Use 4-space indentation and PEP 8 naming:
  - modules/functions: `snake_case`
  - classes: `PascalCase`
  - constants: `UPPER_SNAKE_CASE`
- Use Google-style docstrings consistently for all public modules, classes, functions, and methods. Example:
  ```python
  def get_depth(symbol: str, limit: int | None = None) -> dict[str, object]:
      """Fetch an order book snapshot.

      Args:
          symbol: Market symbol such as ``BTCUSDT``.
          limit: Maximum number of price levels to request.

      Returns:
          Parsed REST payload as a dictionary.

      Raises:
          AsterHttpError: Raised when the HTTP request fails.
      """
  ```

## Testing Guidelines
When adding tests:
- Follow strict test-driven development (TDD): write a failing test first, implement the smallest change to pass, then refactor safely.
- Place them under `tests/` mirroring package paths.
- Name files `test_<unit>.py` and test functions `test_<behavior>()`.
- Run `uv run pytest` locally before handing off changes.

## Commit & Pull Request Guidelines
Write rich Git commit messages that explain the change clearly. Use a descriptive subject and add context in the body when the rationale, scope, or API impact is not obvious:
- Keep the subject line clear, and add enough detail in the body when the change needs extra explanation.
- Group related changes in one commit; avoid mixing refactors and behavior changes.
- Agent workflow policy: the agent may stage and commit changes, but must never run `git push`.
- Push workflow policy: the user performs push manually after reviewing the commit and diff.
- PR workflow policy: the user creates pull requests manually; the agent must not create PRs.
- If there are any questions or ambiguities about the implementation approach or specification, ask the user for clarification before proceeding.
