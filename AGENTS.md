# Repository Guidelines

## Project Structure & Module Organization
The repo centers on the CLI in `chat_cli.py`, which drives conversations against a vLLM-hosted GPT-OSS model. `main.py` is a minimal entry point for future packaging. Project metadata and dependencies live in `pyproject.toml` and `uv.lock`; keep new modules discoverable by adding them under a `src/` package and importing in the CLI. Place integration fixtures or sample transcripts under `gpt_oss_chat_*.json` (ignored by Git) so they remain optional artifacts.

## Build, Test, and Development Commands
Run `uv sync` once to install the pinned dependencies. `uv run chat_cli.py --responses` launches the safer single-turn mode; omit `--responses` to enable streaming. Use `uv run python main.py` to sanity-check packaging, and `uv run python -m compileall chat_cli.py` before release to catch syntax regressions.

## Coding Style & Naming Conventions
Write Python 3.13 compatible code with 4-space indentation and `snake_case` functions. Prefer type hints, explicit imports, and guard CLI entry points with `if __name__ == "__main__"`. Keep module-level constants uppercase (`DEFAULT_BASE_URL`) and reuse existing naming patterns for environment variables (`VLLM_*`). Always open files with `encoding="utf-8"`.

## Testing Guidelines
A formal test suite is not yet in place. When adding functionality, create `tests/` with `pytest` and cover both CLI flag parsing and API interaction shims. Name tests `test_<feature>()` and run them with `uv run pytest`. For manual verification, record a transcript via `/save` and compare responses before merging.

## Commit & Pull Request Guidelines
Follow the existing Git history: short, imperative commit subjects (`update readme`). Squash fixup commits locally and keep messages focused on user-facing change. Pull requests should explain the motivation, link to tracking issues, include example CLI output or transcripts, and call out any new environment variables or credentials.

## Configuration Tips
Set `OPENAI_API_KEY`, `VLLM_BASE_URL`, and `VLLM_MODEL` in your shell before running the CLI; provide local defaults in `.envrc` or export commands, but do not commit secrets. Use `/reset` and `/save` in the CLI to keep iterative runs tidy.
