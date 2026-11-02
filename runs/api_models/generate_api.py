"""Generate the replies of a commercial model through its API, for `runs/run.py --import`.

usage: python generate_api.py MODEL REQUESTS REPLIES --budget USD [--temperature T|none] [--workers N]

MODEL is gpt-6-luna or gemini-3.8-flash. REQUESTS is the file that `runs/run.py MODEL --export REQUESTS`
wrote; REPLIES gets one line per prompt and sample. The API key is read from OPENAI_API_KEY or
GEMINI_API_KEY and is never printed or written.

Settings: the prompt is the only message, one request per sample, at most 2,048 output tokens.
  gpt-6-luna        Chat Completions, reasoning effort none (no hidden reasoning), temperature 0.2
  gemini-3.8-flash  generateContent, thinking level low (the lowest the model accepts; its thinking tokens
                    are billed as output and count toward the output limit), temperature 0.2
--temperature overrides the temperature; `none` leaves it to the provider's default (Section 4.2).

Budget: the cost of every reply is computed from the token counts that the API reports and the standard
prices in PRICES (USD per million tokens). Before each request, the cost so far (including earlier lines
of REPLIES) plus the most that the request can cost must stay within --budget; otherwise no further request
is sent. Rate limits and server errors are retried with a growing pause; any other error, such as an
unsupported parameter or exhausted credit, stops the script with the API's message, so that a
misconfigured request is not repeated. Lines already in REPLIES are skipped, so a run can be resumed.
The settings, prices, number of calls, cost and the dates of the calls are written to REPLIES.meta.json.
"""
import argparse
import json
import math
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

import requests

MAX_OUTPUT_TOKENS = 2048
PRICES = {"gpt-6-luna": (0.10, 0.50), "gemini-3.8-flash": (0.75, 3.75)}  # standard, through Dec 31, 2026
SETTINGS = {"gpt-6-luna": {"endpoint": "https://api.openai.com/v1/chat/completions", "key": "OPENAI_API_KEY",
                           "reasoning_effort": "none", "temperature": 0.2},
            "gemini-3.8-flash": {"endpoint": "https://generativelanguage.googleapis.com/v1beta/models/"
                                             "gemini-3.8-flash:generateContent",
                                 "key": "GEMINI_API_KEY", "thinking_level": "low", "temperature": 0.2}}
RETRY = {429, 500, 502, 503, 504}
TRIES = 6


class Stop(Exception):
    pass


def openai_request(model, settings, prompt):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "reasoning_effort": settings["reasoning_effort"], "max_completion_tokens": MAX_OUTPUT_TOKENS}
    if settings["temperature"] is not None:
        body["temperature"] = settings["temperature"]
    return {"Authorization": f"Bearer {os.environ[settings['key']]}"}, body


def openai_reply(data):
    choice = data["choices"][0]
    usage = data["usage"]
    details = usage.get("completion_tokens_details") or {}
    return {"text": choice["message"].get("content") or "", "stop": choice.get("finish_reason", ""),
            "input_tokens": usage["prompt_tokens"], "output_tokens": usage["completion_tokens"],
            "reasoning_tokens": details.get("reasoning_tokens", 0)}


def gemini_request(model, settings, prompt):
    config = {"maxOutputTokens": MAX_OUTPUT_TOKENS, "thinkingConfig": {"thinkingLevel": settings["thinking_level"]}}
    if settings["temperature"] is not None:
        config["temperature"] = settings["temperature"]
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": config}
    return {"x-goog-api-key": os.environ[settings["key"]]}, body


def gemini_reply(data):
    usage = data.get("usageMetadata", {})
    candidates = data.get("candidates") or [{}]
    parts = (candidates[0].get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    thoughts = usage.get("thoughtsTokenCount", 0)
    return {"text": text, "stop": candidates[0].get("finishReason", data.get("promptFeedback", {}).get("blockReason", "")),
            "input_tokens": usage.get("promptTokenCount", 0),
            "output_tokens": usage.get("candidatesTokenCount", 0) + thoughts, "reasoning_tokens": thoughts}


PROVIDERS = {"gpt-6-luna": (openai_request, openai_reply), "gemini-3.8-flash": (gemini_request, gemini_reply)}


def cost(model, input_tokens, output_tokens):
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1e6


def call(model, settings, prompt):
    make, parse = PROVIDERS[model]
    headers, body = make(model, settings, prompt)
    pause = 2.0
    for attempt in range(TRIES):
        start = time.time()
        try:
            r = requests.post(settings["endpoint"], headers={**headers, "Content-Type": "application/json"},
                              json=body, timeout=180)
        except requests.RequestException as e:
            status, message = None, f"{type(e).__name__}"
        else:
            if r.ok:
                reply = parse(r.json())
                reply["seconds"] = round(time.time() - start, 2)
                return reply
            status, message = r.status_code, r.text[:500]
            if status == 429 and "insufficient_quota" in message:
                raise Stop(f"HTTP 429, credit exhausted: {message}")
            if status not in RETRY:
                raise Stop(f"HTTP {status}: {message}")
        if attempt == TRIES - 1:
            raise Stop(f"gave up after {TRIES} tries; last error: HTTP {status}: {message}")
        print(f"HTTP {status}: {message[:120]} -- retrying in {pause:.0f} s", flush=True)
        time.sleep(pause)
        pause *= 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", choices=sorted(PROVIDERS))
    ap.add_argument("requests")
    ap.add_argument("replies")
    ap.add_argument("--budget", type=float, required=True, help="USD for this replies file, earlier lines included")
    ap.add_argument("--temperature", help="a number, or none for the provider's default")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    settings = dict(SETTINGS[a.model])
    if a.temperature is not None:
        settings["temperature"] = None if a.temperature.lower() == "none" else float(a.temperature)
    if not os.environ.get(settings["key"]):
        raise SystemExit(f"{settings['key']} is not set")

    with open(a.requests, encoding="utf-8") as f:
        requests_ = [json.loads(line) for line in f if line.strip()]
    done, spent = set(), 0.0
    if os.path.exists(a.replies):
        with open(a.replies, encoding="utf-8") as f:
            for r in map(json.loads, filter(str.strip, f)):
                done.add((r["prompt_id"], r["sample"]))
                spent += r["cost"]
    todo = [(r, s) for r in requests_ for s in r["samples"] if (r["prompt_id"], s) not in done]
    print(f"{len(todo)} samples to generate; USD {spent:.4f} spent on this file so far, budget USD {a.budget:.2f}")
    if not todo:
        return

    meta_path = a.replies + ".meta.json"
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {"calls": 0, "cost": 0.0}
    meta.update({"model": a.model, "settings": {k: v for k, v in settings.items() if k != "key"},
                 "max_output_tokens": MAX_OUTPUT_TOKENS, "prices_usd_per_million": PRICES[a.model]})
    meta.setdefault("first_call", datetime.now(timezone.utc).isoformat(timespec="seconds"))

    lock = threading.Lock()
    state = {"spent": spent, "reserved": 0.0, "stop": None, "calls": 0}

    def worst(prompt):
        return cost(a.model, math.ceil(len(prompt) / 2), MAX_OUTPUT_TOKENS)

    def work(item):
        r, s = item
        w = worst(r["text"])
        with lock:
            if state["stop"]:
                return None
            if state["spent"] + state["reserved"] + w > a.budget:
                state["stop"] = state["stop"] or "budget reached"
                return None
            state["reserved"] += w
        try:
            reply = call(a.model, settings, r["text"])
        except Stop as e:
            with lock:
                state["reserved"] -= w
                state["stop"] = state["stop"] or str(e)
            return None
        c = cost(a.model, reply["input_tokens"], reply["output_tokens"])
        line = {"model": a.model, "prompt_id": r["prompt_id"], "sample": s, "case": r["case"], **reply, "cost": c}
        with lock:
            state["reserved"] -= w
            state["spent"] += c
            state["calls"] += 1
            out.write(json.dumps(line) + "\n")
            out.flush()
            meta["calls"] += 1
            meta["cost"] += c
            meta["last_call"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=1)
            if state["calls"] % 100 == 0:
                print(f"{state['calls']} replies, USD {state['spent']:.4f} spent")
        return line

    with open(a.replies, "a", encoding="utf-8") as out, ThreadPoolExecutor(a.workers) as pool:
        list(pool.map(work, todo))
    print(f"{state['calls']} replies written, USD {state['spent']:.4f} spent on this file in total")
    if state["stop"]:
        print(f"stopped: {state['stop']}")


if __name__ == "__main__":
    main()
