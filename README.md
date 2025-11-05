# CLI Chat Interface for GPT-OSS

`chat_cli.py` provides a terminal front-end for running GPT-OSS models exposed through a vLLM server. It speaks the OpenAI-compatible APIs offered by vLLM and adds conveniences for system prompts, transcripts, and session management.

## Prerequisites

- Install dependencies pinned in `pyproject.toml` with `uv sync`.
- Start a vLLM server that serves the GPT-OSS model you want to use, for example:
  ```bash
  uv run vllm serve openai/gpt-oss-120b
  ```
- Export the connection details expected by the CLI:
  - `OPENAI_API_KEY` (use a placeholder if your server does not enforce auth).
  - `VLLM_BASE_URL` (defaults to `http://localhost:8000/v1`).
  - `VLLM_MODEL` (defaults to `openai/gpt-oss-120b`).
  - Optional `VLLM_SYSTEM` to set a different default system prompt.

## Quick Start

1. Launch the CLI in single-turn mode to avoid streaming quirks currently seen with GPT-OSS:
   ```bash
   uv run chat_cli.py --responses
   ```
2. Drop `--responses` to use the Chat Completions API instead. Add `--no-stream` if you want full responses printed after each turn.
3. Use `/exit` (or `Ctrl+C`) to leave the session when you are done.

## CLI Options

- `--base-url`: Override the vLLM base URL (defaults to `VLLM_BASE_URL` or `http://localhost:8000/v1`).
- `--model`: Choose the model to query (defaults to `VLLM_MODEL` or `openai/gpt-oss-120b`).
- `--system`: Provide the initial system prompt. When `--responses` is disabled, the prompt is sent as the first chat message.
- `--transcript`: Load an existing JSON transcript before chatting and write the updated transcript on exit.
- `--no-stream`: Disable incremental output and print the assistant reply only after the turn completes.
- `--responses`: Route requests through the Responses API for safer, non-streaming single-turn interactions.

## In-Session Commands

Once the banner appears you can type messages or use the built-in commands:

- `/reset` clears the conversation state (the system prompt is re-applied when relevant).
- `/system <text>` updates the system prompt mid-session.
- `/save <path>` writes the current transcript to the given JSON file. When no path is provided the CLI generates `gpt_oss_chat_<timestamp>.json` in the current directory.
- `/exit` or `/quit` ends the chat loop immediately.

## Transcript Workflow

Pass `--transcript <path>` to continue from a saved conversation. The CLI loads the previous messages at startup and will overwrite the file with the latest transcript when you exit cleanly. You can also use `/save` at any point to snapshot the conversation to a different file, making it easy to collect sample transcripts (ignored by Git thanks to the `gpt_oss_chat_*.json` pattern).

## Additional Tips

- `uv run python main.py` invokes the minimal packaging entry point to sanity-check distribution metadata.
- Run `uv run python -m compileall chat_cli.py` before publishing to catch syntax regressions.
