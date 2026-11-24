"""Lab 2, Steps 3-5: a ReAct agent from scratch (no framework).

    python lab02/react_agent.py "I have GHS 1,200 ..."      # one question
    python lab02/react_agent.py                              # run the six lab questions

Each run's full trace is saved to lab02/evidence/trace_<n>.txt.
"""
import json
import os
import re
import sys
import time
from pathlib import Path

import litellm
from dotenv import load_dotenv
from litellm import completion

from tools import TOOLS

litellm.suppress_debug_info = True  # hide LiteLLM's "Give Feedback" banner on handled errors

HERE = Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows console (cp1252) safety
load_dotenv()
MODEL = os.getenv("LLM_MODEL")

SYSTEM_PROMPT = """You are a helpful assistant for a trader at Makola Market. You answer questions
about costing and quick facts by reasoning step by step and using tools.

You have NO function-calling ability. You use tools only by WRITING plain text in the format
below; the program reads your text, runs the tool and replies. Never emit a JSON tool call.

Tools (text actions):
- calculator: evaluates an arithmetic expression using + - * / and brackets. Input: the expression only, e.g. 4*185 + 3*95
- wiki_lookup: returns the summary of a Wikipedia page. Input: the exact page title, e.g. Bono East Region
- finish: ends the task. Input: the final answer for the user.

On EVERY step reply in exactly this format and nothing else:
Thought: <your reasoning>
Action: calculator | wiki_lookup | finish
Action Input: <input for the tool, or the final answer if finish>

Rules:
- Write only ONE Thought/Action/Action Input per reply, then stop. The system will reply with
  "Observation: <result>".
- Never do arithmetic in your head: use the calculator for every calculation.
- Use wiki_lookup for facts you are not certain of. If a page is not found, try a better title
  once, then answer honestly that you could not find it.
- If the question needs no tool, use finish straight away."""

ACTION_RE = re.compile(r"Action:\s*(\w+)\s*\nAction Input:\s*(.*)", re.DOTALL)

FORMAT_REMINDER = ("Observation: I could not parse your reply. Reply in exactly this format:\n"
                   "Thought: <your reasoning>\nAction: calculator | wiki_lookup | finish\n"
                   "Action Input: <input>\n"
                   "If you already know the answer, use Action: finish with the answer as Action Input.")


def parse(text):
    m = ACTION_RE.search(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


FAILED_GEN_RE = re.compile(r'"failed_generation"\s*:\s*"((?:[^"\\]|\\.)*)"')


CALL_RE = re.compile(r'"name"\s*:\s*"([^"]*)"\s*,\s*"arguments"\s*:\s*(.*)\}\s*$', re.DOTALL)


def _first_value(args):
    """The model's arguments may be a dict, a JSON string holding a dict, a number or bare text."""
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except ValueError:
            return args.strip().strip('"')
    if isinstance(args, dict):
        return str(next(iter(args.values()), "")) if args else ""
    return str(args)


def recover_native_tool_call(err_text):
    """gpt-oss on Groq is trained for native function calling. Even when we declare no tools it
    often emits a JSON tool call, which Groq rejects with HTTP 400 'tool_use_failed' and returns in
    'failed_generation'. Rebuild the intended action in our text protocol so the loop can go on."""
    m = FAILED_GEN_RE.search(err_text)
    if not m:
        return None
    try:
        gen = json.loads(f'"{m.group(1)}"')  # unescape the string
    except ValueError:
        return None
    try:
        call = json.loads(gen)
        name, args = call.get("name", ""), call.get("arguments", "")
    except (ValueError, AttributeError):
        cm = CALL_RE.search(gen)  # e.g. {"name": "calculator", "arguments": 760-1000}
        if not cm:
            return None
        name, args = cm.group(1), cm.group(2).strip()
    return (f"Thought: (recovered from a native tool call)\n"
            f"Action: {name}\nAction Input: {_first_value(args)}")


def _retry_after(err_text, attempt):
    m = re.search(r"try again in ([\d.]+)s", err_text)
    return float(m.group(1)) + 1 if m else 5 * (attempt + 1)


def call_model(messages, retries=4):
    """One model call, stopping before the model can invent an Observation.
    Returns (reply_text, tokens, note). Retries with a growing pause on rate limits."""
    for attempt in range(retries):
        try:
            resp = completion(model=MODEL, messages=messages, temperature=0,
                              stop=["Observation:"])
            return (resp.choices[0].message.content or "").strip(), resp.usage.total_tokens, None
        except Exception as e:  # noqa: BLE001
            text = str(e)
            if "tool_use_failed" in text:
                recovered = recover_native_tool_call(text)
                if recovered:
                    return recovered, 0, "[recovered: model emitted a native tool call (tool_use_failed)]"
            if "RateLimit" in e.__class__.__name__ and attempt < retries - 1:
                time.sleep(_retry_after(text, attempt))  # free tier: wait as Groq asks
                continue
            raise


def run_agent(question, max_steps=6, trace_path=None):
    messages = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Question: {question}"}]
    trace = [f"Model: {MODEL}", f"Question: {question}", ""]
    total_tokens = 0
    answer = None
    seen = set()  # (action, input) pairs already run: guard against repeat loops

    def log(line):
        print(line)
        trace.append(line)

    for step in range(1, max_steps + 1):
        log(f"--- Step {step} ---")
        try:
            reply, tokens, note = call_model(messages)
        except Exception as e:  # noqa: BLE001  never crash the loop
            log(f"Model error: {e.__class__.__name__}: {str(e)[:300]}")
            log("Stopped: the model call failed.")
            break
        total_tokens += tokens
        if note:
            log(note)
        log(reply if reply else "(empty reply)")
        messages.append({"role": "assistant", "content": reply})

        action, action_input = parse(reply)
        if action is None:
            # Reactive error handling: unparseable reply -> corrective observation.
            obs = FORMAT_REMINDER
        elif action == "finish":
            answer = action_input
            break
        elif action not in TOOLS:
            obs = (f"Observation: Unknown action '{action}'. "
                   f"Valid actions are: {', '.join(TOOLS)}, finish.")
        else:
            # Keep only the first line of input in case the model kept writing.
            tool_input = action_input.split("\n")[0].strip()
            key = (action, tool_input.lower())
            if key in seen:
                # Reactive rule: an identical repeat cannot give new information.
                obs = (f"Observation: You already ran {action} with '{tool_input}' and saw the result "
                       "above. Repeating it gives nothing new. Try a different input, or if you "
                       "cannot find the information, use finish and say so honestly.")
            else:
                seen.add(key)
                obs = f"Observation: {TOOLS[action](tool_input)}"
        log(obs)
        messages.append({"role": "user", "content": obs})
    else:
        log(f"Stopped: reached max_steps={max_steps} without a finish action.")

    log("")
    log(f"Final answer: {answer if answer is not None else '(none, agent did not finish)'}")
    log(f"Total tokens: {total_tokens}")
    if trace_path:
        Path(trace_path).write_text("\n".join(trace) + "\n", encoding="utf-8")
    return answer


QUESTIONS = [
    # 1. Step 4: the budget question
    "I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each. "
    "How much will I have left?",
    # 2-3. Step 5: need both tools
    "What is the capital of the Bono East Region, and if I send 12 boxes of tomatoes there at "
    "GHS 340 per box plus GHS 450 transport, what is my total cost?",
    "In what year was Ghana's cedi introduced? How many years ago was that from 2026?",
    # 4. Step 5: Wikipedia page that does not exist
    "Look up the Wikipedia page for 'Makola Market Traders Union of Ashanti Region 1983' and summarise it.",
    # 5. Step 5: needs no tool
    "Hello! What can you help me with?",
    # 6. Step 5: deliberately badly worded
    "pls 3 bag sugar 210 each n 2 crate egg 65 i got 1000 cedi wat remain",
]


if __name__ == "__main__":
    if not MODEL:
        sys.exit("LLM_MODEL is not set. Copy .env.example to .env and set LLM_MODEL.")
    evidence = HERE / "evidence"
    if len(sys.argv) > 1:
        n = len(list(evidence.glob("trace_*.txt"))) + 1
        run_agent(" ".join(sys.argv[1:]), trace_path=evidence / f"trace_{n}.txt")
    else:
        for i, q in enumerate(QUESTIONS, 1):
            print(f"\n==================== Question {i} ====================")
            run_agent(q, trace_path=evidence / f"trace_{i}.txt")
            time.sleep(10)  # stay inside the free-tier tokens-per-minute limit (8,000 TPM)
