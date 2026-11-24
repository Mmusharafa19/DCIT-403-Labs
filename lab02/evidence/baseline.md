# Lab 2, Step 1: Baseline (the model on its own, no tools)

Model: `groq/openai/gpt-oss-20b`, default temperature, no tools. Script: `lab02/baseline.py`.
Raw output: `baseline_raw.txt`.

## Budget question (asked three times)

> I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at GHS 95 each.
> How much will I have left?

Correct answer: 4 × 185 + 3 × 95 = 740 + 285 = 1,025; 1,200 − 1,025 = **GHS 175**.

| Run | Model's answer | Correct? |
|---|---|---|
| 1 | "175 GHS. 1200 − (4 × 185 + 3 × 95) = 175" | ✅ Correct |
| 2 | "GHS 175. 4×185 + 3×95 = 740 + 285 = 1025; 1200 – 1025 = 175." | ✅ Correct |
| 3 | "175 GHS. 1200 - (4*185 + 3*95) = 175" | ✅ Correct |

## Factual questions

| # | Question | Model's answer | Correct? | How confident it sounded |
|---|---|---|---|---|
| 1 | What is the capital of the Bono East Region of Ghana? | "The capital of Ghana's Bono East Region is Techiman." | ✅ Correct (confirmed by `wiki_lookup("Bono East Region")`) | Fully confident, no hedging |
| 2 | In what year was the Ghanaian cedi first introduced, and what currency did it replace? | "…first introduced in 1965, replacing the Ghanaian pound." | ✅ Correct | Fully confident, no hedging |

## Observations

- **Baseline accuracy: 5/5.** gpt-oss-20b is a *reasoning* model (it spends hidden "reasoning tokens"
  before answering, as the `usage` output in Lab 1 showed), so small arithmetic like this is within its reach.
  The lab's expected "the model gets the arithmetic wrong" result did not appear with this model.
- The model sounds equally confident whether or not it could actually check: it gives no source and no
  hedging. With the model alone, a trader cannot tell a correct answer from a confident wrong one.
  The ReAct agent's value is therefore **verifiability**: every number comes from the calculator and every
  fact from a Wikipedia observation that appears in the trace.
- The ReAct agent did not always beat the baseline. On the badly worded question (trace 6) the agent
  produced a **wrong** answer, because the model chose the wrong expression for the calculator (see
  `traces_summary.md`).
