# Lab 2: Trace Summary

Model: `groq/openai/gpt-oss-20b`, temperature 0, `max_steps=6`, `stop=["Observation:"]`.
Run with `python lab02/react_agent.py` (all six) or `python lab02/react_agent.py "<question>"`.

| Trace | Question type | Question | Steps | Final answer | Correct? |
|---|---|---|---|---|---|
| `trace_1.txt` | Budget (Step 4) | GHS 1,200; 4 rice @ 185, 3 oil @ 95: how much left? | 5 | GHS 175 | ✅ |
| `trace_2.txt` | Both tools | Capital of Bono East + 12 boxes @ 340 + 450 transport | 5 | Techiman, GHS 4,530 | ✅ |
| `trace_3.txt` | Both tools | Year the cedi was introduced; years ago from 2026 | 1 | 1965, 61 years | ✅ value, but answered from memory with no tool (breaks the "always use the calculator" rule) |
| `trace_4.txt` | Missing Wikipedia page | "Makola Market Traders Union of Ashanti Region 1983" | 3 | Honest "could not find" | ✅ (tried a related title first) |
| `trace_5.txt` | No tool needed | "Hello! What can you help me with?" | 1 | "User asks what I can help with. No tool needed." | ⚠️ Did not crash, but the finish input is the model's own note, not a greeting for the user |
| `trace_6.txt` | Badly worded | "pls 3 bag sugar 210 each n 2 crate egg 65 i got 1000 cedi wat remain" | 4 | "You would need an additional 240 cedis" | ❌ Correct is **GHS 240 left** |
| `trace_7.txt` | Both tools (re-run of Q3) | Same as trace 3 | 5 | 1965, 61 years | ✅ Loop guard fired at step 3 |

None of the runs crashed (Step 5 checkpoint). Every failure kind in Step 5 occurs at least once and is handled:
unparseable reply (traces 1, 2, 6, 7), unknown action (`before_loop_guard/trace_2.txt` in an earlier run:
`Unknown action 'assistant'`), and reaching max_steps (`before_loop_guard/trace_2.txt`, `trace_3.txt`).

## Failures and fixes

### Failure 1: crash on step 1 (`failure_1_tool_use_failed.txt`)
- **What:** The first run crashed with `BadRequestError ... "code":"tool_use_failed"`.
- **Cause:** gpt-oss-20b is trained for *native* function calling. Reading a list of tools in the system
  prompt, it emitted a JSON tool call (`{"name": "calculator", "arguments": {"expression": "4*185 + 3*95"}}`)
  instead of the text protocol. We declared no tools, so Groq rejected the reply (HTTP 400), and the exception
  escaped the loop. The model's *decision* was right; only the *format* was wrong.
- **Tried first (did not work):** prompt changes ("you have NO function-calling ability… never emit a JSON tool
  call"), a few-shot example, avoiding the word "tool", removing `stop`, changing `reasoning_effort`. 0 of 21
  test calls produced text on the first step. The behaviour is in the model, not the prompt.
- **Fix (reactive error handling):** `call_model()` catches `tool_use_failed`, reads the attempted call from
  `failed_generation` and converts it to `Action:` / `Action Input:` text (`recover_native_tool_call()`), so the
  loop continues. The parser accepts any `arguments` shape (object, number, bare text such as `760-1000`).
  Any other model error is logged and ends the run cleanly instead of crashing.

### Failure 2: repeat loop until max_steps (`before_loop_guard/trace_3.txt`)
- **What:** For the cedi question the agent called `wiki_lookup("Cedi")` four times. The summary does not
  contain the year, so the agent ran out of steps.
- **Cause:** A purely reactive policy: the same percept produced the same action, with no memory that it had
  already failed. The recovered native calls carry no Thought, so the model's plan is not visible in the history.
- **Fix:** A loop guard. The agent remembers each `(action, input)` pair; an identical repeat is not run, and
  the Observation tells the model to try something different or finish honestly. Re-run (`trace_7.txt`): the guard
  fired at step 3, the agent tried another title, then finished at step 5. The format reminder now also says
  "If you already know the answer, use Action: finish", which fixed the max_steps run in
  `before_loop_guard/trace_2.txt` (now `trace_2.txt`, finished at step 5).

### Failure 3 (open): wrong subtraction order (`trace_6.txt`)
- The model asked the calculator for `760-1000` rather than `1000-760`, got `-240` and concluded the trader is
  short GHS 240. The calculator was correct; the *deliberative* step (choosing what to compute) was wrong.
  Tools make arithmetic exact, but they cannot fix a wrong plan. Possible fixes: ask the model to restate the
  question as an equation in its Thought before calling the calculator, or add a check that "how much is
  left" answers are not negative without a warning.
