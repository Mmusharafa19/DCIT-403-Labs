# AI-Use Log

Add one row every time you use an AI tool for lab work (see Lab Manual Section 4).
Copy the rows for each lab into that lab's report.

| Date | Lab | Tool | What I asked | What I used | What I changed or checked |
|---|---|---|---|---|---|
| 23 Nov 2026 | Setup | Claude Code (Opus 5.5) | Install LiteLLM and set up `.env` with my Groq key | Upgraded pip (22.3 got stuck resolving), installed litellm 1.110.2; `.env` with `LLM_MODEL` and `GROQ_API_KEY` | Ran `scripts/check_setup.py --call`: model replied "ready"; confirmed `.env` is git-ignored. Groq free limits for gpt-oss-20b (from the guide): ~30 RPM, 1,000 RPD, 8,000 TPM, 200,000 TPD |
| 23 Nov 2026 | Lab 1 | Claude Code (Opus 5.5) | Complete Lab 1 from the manual: hello_llm, PEAS, facts, campus_bot, tests, diagnostic, concept check | All Lab 1 files and evidence | _To do: re-read every file, check I can explain each line, and rewrite the concept-check answers and PEAS in my own words_ |
| 23 Nov 2026 | Lab 1 | Claude Code (Opus 5.5) | Fix crash `UnicodeEncodeError '\u202f'` in campus_bot | `sys.stdout.reconfigure(encoding="utf-8")` | Re-ran the 5-turn conversation: no crash |
| 23 Nov 2026 | Lab 2 | Claude Code (Opus 5.5) | Complete Lab 2: baseline, tools, ReAct agent, traces, concept check | All Lab 2 files and evidence | _To do: re-read every file and check I can explain each line_ |
| 23 Nov 2026 | Lab 2 | Claude Code (Opus 5.5) | Why the agent crashes with Groq `tool_use_failed` | Diagnosis (gpt-oss emits native tool calls) + `recover_native_tool_call()` | Tested 7 prompt/parameter variants (none fixed it); unit-checked the parser on 3 failed generations; re-ran all six questions without a crash |
