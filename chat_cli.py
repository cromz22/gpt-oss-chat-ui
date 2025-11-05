#!/usr/bin/env python3
import argparse, json, os, sys
from datetime import datetime
from openai import OpenAI

DEFAULT_BASE_URL = os.environ.get("VLLM_BASE_URL", "http://localhost:8000/v1")
DEFAULT_MODEL = os.environ.get("VLLM_MODEL", "openai/gpt-oss-120b")
DEFAULT_SYSTEM = os.environ.get("VLLM_SYSTEM", "You are a helpful assistant.")

BANNER = f"""\
gpt-oss CLI (vLLM)
- base_url: {DEFAULT_BASE_URL}
- model   : {DEFAULT_MODEL}
Type your message and press Enter.
Commands: /reset, /system <text>, /save <path>, /exit
"""

def ensure_parent_dir(path: str) -> None:
    """Create the parent directory for path if it does not exist."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

def respond_via_chat(client: OpenAI, model: str, messages: list[dict]) -> str:
    """Single assistant turn via Chat Completions API (non-streaming)."""
    resp = client.chat.completions.create(model=model, messages=messages)
    text = resp.choices[0].message.content or ""
    print(text)
    return text

def respond_via_responses(client: OpenAI, model: str, system: str | None, user_text: str) -> str:
    """Single-turn via Responses API (non-streaming). Safer with GPT-OSS on vLLM."""
    # We pass instructions (system) separately and put the user text in input.
    resp = client.responses.create(
        model=model,
        instructions=system or "You are a helpful assistant.",
        input=user_text,
    )
    out = resp.output_text or ""
    print(out)
    return out

def main():
    p = argparse.ArgumentParser(description="CLI chat for gpt-oss via vLLM.")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL)
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--system", default=DEFAULT_SYSTEM)
    p.add_argument("--transcript", default=None)
    p.add_argument("--responses", action="store_true",
                   help="Use Responses API (non-streaming).")
    args = p.parse_args()

    client = OpenAI(base_url=args.base_url, api_key=os.environ.get("OPENAI_API_KEY", "EMPTY"))

    messages: list[dict] = []
    if not args.responses and args.system:
        messages.append({"role": "system", "content": args.system})

    if args.transcript and os.path.exists(args.transcript):
        try:
            with open(args.transcript, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            prior = loaded["messages"] if isinstance(loaded, dict) and "messages" in loaded else loaded
            if isinstance(prior, list):
                messages = prior
                print(f"Loaded {len(messages)} messages from {args.transcript}")
        except Exception as e:
            print(f"Warning: failed to load transcript: {e}")

    print(BANNER)

    while True:
        try:
            user = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEnd of chat")
            break

        if not user:
            continue

        if user.lower() in ("/exit", "/quit"):
            print("Bye!")
            break
        if user.startswith("/reset"):
            messages = []
            if not args.responses and args.system:
                messages.append({"role": "system", "content": args.system})
            print("Conversation reset.")
            continue
        if user.startswith("/system"):
            new_sys = user[len("/system"):].strip()
            if not new_sys:
                print("Usage: /system <text>")
                continue
            args.system = new_sys
            if not args.responses:
                if messages and messages[0]["role"] == "system":
                    messages[0]["content"] = new_sys
                else:
                    messages.insert(0, {"role": "system", "content": new_sys})
            print("System prompt updated.")
            continue
        if user.startswith("/save"):
            path = user[len("/save"):].strip()
            if not path:
                filename = f"gpt_oss_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                path = os.path.join("outputs", filename)
            try:
                payload = {"model": args.model, "messages": messages}
                ensure_parent_dir(path)
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False, indent=2)
                print(f"Saved transcript to {path}")
            except Exception as e:
                print(f"Failed to save transcript: {e}")
            continue

        # Normal turn
        if args.responses:
            # FIX: Responses API path (no streaming, no chat history yet).
            reply = respond_via_responses(client, args.model, args.system, user)
            # Keep a parallel transcript in chat format for saving.
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": args.system})
            messages.append({"role": "user", "content": user})
            messages.append({"role": "assistant", "content": reply})
        else:
            messages.append({"role": "user", "content": user})
            reply = respond_via_chat(client, args.model, messages)
            messages.append({"role": "assistant", "content": reply})

    if args.transcript:
        try:
            ensure_parent_dir(args.transcript)
            with open(args.transcript, "w", encoding="utf-8") as f:
                json.dump({"model": args.model, "messages": messages}, f, ensure_ascii=False, indent=2)
            print(f"Wrote transcript to {args.transcript}")
        except Exception as e:
            print(f"Note: couldn't write transcript to {args.transcript}: {e}")

if __name__ == "__main__":
    main()
