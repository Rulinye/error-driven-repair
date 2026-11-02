"""Generate the replies of an open model on a GPU notebook (Colab or Kaggle), for `runs/run.py --import`.

usage: python generate_open.py MODEL_ID REQUESTS REPLIES [--batch N]

REQUESTS is the file that `runs/run.py MODEL --export REQUESTS` wrote; REPLIES gets one line per prompt and
sample. The prompt is the only message, in the model's own chat format. Sampling follows the model's
generation config, except for the temperature (0.2, Section 4.2) and the length limit (2,048 new tokens).
The model is spread over all GPUs, in bfloat16 on GPUs that compute in it natively (compute capability 8.0
or higher, such as L4 and A100) and in float16 on older ones (T4, P100), which can only emulate bfloat16
and are then several times slower; float32 without a GPU is only useful for testing the script.
--batch is the number of prompts per batch (2 by default; 8 suits Qwen2.5-Coder-7B on 2 x T4).
The model, its tokenizer and its generation config are loaded at the fixed Hugging Face commit in REVISIONS
(see `runs/results/open_model_revisions.json`).

Lines already in REPLIES are skipped, so a session that was cut off can be resumed. If a batch runs out
of GPU memory, it is split, down to one sample at a time. The GPUs, the library versions, the generation
settings (including the sampling parameters in effect) and the GPU time are written to REPLIES.meta.json.
"""
import argparse
import copy
import json
import os
import time

import torch
import transformers
from packaging.version import Version
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

TEMPERATURE = 0.2
MAX_NEW_TOKENS = 2048
SAMPLING = ("do_sample", "temperature", "top_k", "top_p", "min_p", "repetition_penalty", "max_new_tokens")
REVISIONS = {
    "Qwen/Qwen2.5-Coder-7B-Instruct": "c03e6d358207e414f1eca0bb1891e29f1db0e242",
    "codellama/CodeLlama-7b-Instruct-hf": "22cb240e0292b0b5ab4c17ccd97aa3a2f799cbed",
}


def load(model_id):
    if not torch.cuda.is_available():
        dtype = torch.float32
    elif torch.cuda.get_device_capability(0) >= (8, 0):
        dtype = torch.bfloat16
    else:
        dtype = torch.float16
    revision = REVISIONS.get(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    # transformers renamed torch_dtype to dtype in 4.56
    key = "dtype" if Version(transformers.__version__) >= Version("4.56") else "torch_dtype"
    model = AutoModelForCausalLM.from_pretrained(model_id, revision=revision, device_map="auto", **{key: dtype})
    model.eval()
    config = GenerationConfig.from_pretrained(model_id, revision=revision)
    config.do_sample = True
    config.temperature = TEMPERATURE
    config.max_new_tokens = MAX_NEW_TOKENS
    config.pad_token_id = tokenizer.pad_token_id
    if config.eos_token_id is None:
        config.eos_token_id = tokenizer.eos_token_id
    return tokenizer, model, config, dtype


def generate(tokenizer, model, config, items, k):
    """Generate k samples for each (request, samples) item; return a list of reply dicts."""
    texts = [tokenizer.apply_chat_template([{"role": "user", "content": r["text"]}], tokenize=False,
                                           add_generation_prompt=True) for r, _ in items]
    enc = tokenizer(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
    config = copy.deepcopy(config)
    config.num_return_sequences = k
    start = time.time()
    with torch.no_grad():
        out = model.generate(**enc, generation_config=config)
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    seconds = time.time() - start
    eos = config.eos_token_id if isinstance(config.eos_token_id, list) else [config.eos_token_id]
    width = enc["input_ids"].shape[1]
    replies = []
    for i, (r, samples) in enumerate(items):
        n_in = int(enc["attention_mask"][i].sum())
        for j, s in enumerate(samples):
            seq = out[i * k + j, width:].tolist()
            ends = [n for n, t in enumerate(seq) if t in eos]
            n_out = ends[0] + 1 if ends else len(seq)
            replies.append({"prompt_id": r["prompt_id"], "sample": s, "case": r["case"],
                            "text": tokenizer.decode(seq[:n_out], skip_special_tokens=True),
                            "input_tokens": n_in, "output_tokens": n_out, "stop": "stop" if ends else "length",
                            "gpu_seconds": seconds / (len(items) * k)})
    return replies


def generate_safely(tokenizer, model, config, items, k):
    """generate(), splitting the batch when the GPU runs out of memory."""
    try:
        return generate(tokenizer, model, config, items, k)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        if len(items) > 1:
            half = len(items) // 2
            return (generate_safely(tokenizer, model, config, items[:half], k)
                    + generate_safely(tokenizer, model, config, items[half:], k))
        if k > 1:
            r, samples = items[0]
            return [x for s in samples for x in generate_safely(tokenizer, model, config, [(r, [s])], 1)]
        raise


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model_id")
    ap.add_argument("requests")
    ap.add_argument("replies")
    ap.add_argument("--batch", type=int, default=2, help="prompts per batch")
    a = ap.parse_args()

    with open(a.requests, encoding="utf-8") as f:
        requests = [json.loads(line) for line in f if line.strip()]
    done = set()
    if os.path.exists(a.replies):
        with open(a.replies, encoding="utf-8") as f:
            done = {(r["prompt_id"], r["sample"]) for r in map(json.loads, filter(str.strip, f))}
    todo = [(r, [s for s in r["samples"] if (r["prompt_id"], s) not in done]) for r in requests]
    todo = [(r, ss) for r, ss in todo if ss]
    print(f"{len(todo)} prompts, {sum(len(ss) for _, ss in todo)} samples to generate")
    if not todo:
        return

    tokenizer, model, config, dtype = load(a.model_id)
    meta_path = a.replies + ".meta.json"
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.exists(meta_path) else {"gpu_seconds": 0.0}
    meta.update({"model": a.model_id, "revision": REVISIONS.get(a.model_id),
                 "dtype": str(dtype).replace("torch.", ""),
                 "gpus": [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())] or ["none"],
                 "compute_capability": ".".join(map(str, torch.cuda.get_device_capability(0)))
                 if torch.cuda.is_available() else "none",
                 "batch": a.batch, "torch": torch.__version__, "transformers": transformers.__version__,
                 "sampling": {x: getattr(config, x, None) for x in SAMPLING},
                 "generation": {x: v for x, v in config.to_dict().items() if v is not None}})

    # batches of prompts that need the same number of samples, shortest prompts first
    todo.sort(key=lambda x: (len(x[1]), len(x[0]["text"])))
    batches, current = [], []
    for item in todo:
        if current and (len(current) == a.batch or len(current[0][1]) != len(item[1])):
            batches.append(current)
            current = []
        current.append(item)
    batches.append(current)

    with open(a.replies, "a", encoding="utf-8") as out:
        for n, items in enumerate(batches, 1):
            replies = generate_safely(tokenizer, model, config, items, len(items[0][1]))
            for r in replies:
                out.write(json.dumps(r) + "\n")
            out.flush()
            meta["gpu_seconds"] += sum(r["gpu_seconds"] for r in replies)
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=1)
            if n % 10 == 0 or n == len(batches):
                print(f"batch {n} of {len(batches)}, GPU time so far {meta['gpu_seconds'] / 60:.1f} minutes")


if __name__ == "__main__":
    main()
