# Repository Guidelines
## Project Overview
This project implements a minimal API client for the Aster decentralized exchange (DEX).
The supported scope is intentionally narrow: trading operations, real-time market data streams, and local order book construction. All API-facing functionality should be designed for asynchronous use so the client can be integrated into latency-sensitive trading systems without forcing synchronous wrappers.

Implementation decisions must distinguish between the different API families exposed by Aster (for example, versioned REST surfaces such as v1 and v3) and use the correct behavior for each one. Private API authentication and request signing must be implemented from primary-source documentation with strong attention to correctness, while keeping the signing path efficient and operationally lightweight. Integration tests against live endpoints are out of scope; the project should emphasize deterministic unit tests and protocol-level validation instead.

## Project Structure & Module Organization
Organize the package around clear protocol boundaries so each concern can evolve independently. Keep REST transport, authentication/signing, WebSocket transport, message models, and local order book logic in separate modules. Prefer a thin public client layer that composes these building blocks rather than embedding protocol details in a single large class.

Use a structure that makes version-specific behavior explicit, especially where different Aster API families diverge. WebSocket stream handling should isolate subscription/session management from event parsing and downstream state updates. Local order book construction should live in its own module with focused tests covering snapshot/delta application, sequencing, and recovery behavior. Keep public interfaces small, typed, and async-first.

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
- Write strict type hints anywhere they add clarity to interfaces or state. Public APIs, async boundaries, protocol models, and internal state containers should be fully annotated unless there is a concrete reason not to do so.
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
