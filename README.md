# CLI Chat Interface for GPT-OSS

1. Start a vLLM server on a GPU with more than Hopper capability. Set `HF_HOME` and `CUDA_VISIBLE_DEVICES` if necessary. To install vLLM, see [the official docs](https://docs.vllm.ai/en/stable/getting_started/installation/gpu.html).

    ```
    uv run vllm serve openai/gpt-oss-120b
    ```

1. To chat, run:

    ```
    uv run chat_cli.py --responses
    ```

    - System prompts can be set with `--system "<system prompt>"`.
