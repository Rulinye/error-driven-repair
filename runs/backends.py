"""Model backends for runs/run.py.

A backend turns one prompt into a reply: the text, the input and output tokens (output including any
reasoning tokens, which are billed as output) and why the generation stopped.

  fake   answers with the files of the test case instead of a model, so that the whole pipeline can be
         tested without cost. Sample 0 is the reference fix, sample 1 the wrong fix (the old program
         where the case has none), sample 2 the old program, sample 3 a reply without code, and sample 4
         the reference fix after a bash block. Two of every five samples are therefore correct.

The open models (OPEN, with their Hugging Face ids) and the commercial models (API) are not called from
here: they run on a notebook, with runs/open_models/generate_open.py and runs/api_models/generate_api.py,
between `run.py --export` and `run.py --import`. The commercial models' cost is computed there, from the
token counts that the API reports.

PRICES are USD per million input and output tokens. Only BILLABLE backends count toward the total
budget; the fake backend has a nominal price so that the budget stop can be tested.
"""
import math
import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "..", "test_cases", "cases")

MAX_OUTPUT_TOKENS = 2048
TEMPERATURE = 0.2
OPEN = {"qwen2.5-coder-7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "codellama-7b": "codellama/CodeLlama-7b-Instruct-hf"}
API = {"gpt-6-luna": "OpenAI", "gemini-3.8-flash": "Google"}
PRICES = {"fake": (1.0, 5.0), **{m: (0.0, 0.0) for m in OPEN},
          "gpt-6-luna": (0.10, 0.50), "gemini-3.8-flash": (0.75, 3.75)}  # standard prices through Dec 31, 2026
BILLABLE = set(API)


@dataclass
class Reply:
    text: str
    input_tokens: int
    output_tokens: int
    stop: str


def approx_tokens(text):
    """A rough token count (about four characters per token), used only for estimates."""
    return math.ceil(len(text) / 4)


def _case_file(cid, name):
    path = os.path.join(CASES, cid, name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def fake(prompt, cid, sample):
    fixed, old = _case_file(cid, "fixed.py"), _case_file(cid, "old.py")
    wrong = _case_file(cid, "wrong.py") or old
    text = [f"```python\n{fixed}```",
            f"```python\n{wrong}```",
            f"```python\n{old}```",
            "I cannot fix this code without more information.",
            f"Install the new version first:\n\n```bash\npip install --upgrade pandas numpy\n```\n\n"
            f"Then use:\n\n```python\n{fixed}```"][sample % 5]
    return Reply(text, approx_tokens(prompt), approx_tokens(text), "stop")


BACKENDS = {"fake": fake}


def cost(model, input_tokens, output_tokens):
    price_in, price_out = PRICES[model]
    return (input_tokens * price_in + output_tokens * price_out) / 1e6
