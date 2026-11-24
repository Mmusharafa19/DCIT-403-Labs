"""Lab 2, Step 1: baseline - the model on its own, no tools.
Asks the budget question three times and two factual questions, and prints the raw
answers (copied into evidence/baseline.md and marked correct/incorrect).
"""
import os
import sys

from dotenv import load_dotenv
from litellm import completion

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv()
MODEL = os.getenv("LLM_MODEL")

BUDGET = ("I have GHS 1,200. I want 4 bags of rice at GHS 185 each and 3 gallons of oil at "
          "GHS 95 each. How much will I have left? Reply with the amount and one line of working.")
FACTS = ["What is the capital of the Bono East Region of Ghana? One sentence.",
         "In what year was the Ghanaian cedi first introduced, and what currency did it replace? One sentence."]


def ask(q):
    r = completion(model=MODEL, messages=[{"role": "user", "content": q}])  # default temperature
    return r.choices[0].message.content.strip()


print(f"Model: {MODEL}\n")
for i in range(1, 4):
    print(f"## Budget run {i}\n{ask(BUDGET)}\n")
for i, q in enumerate(FACTS, 1):
    print(f"## Factual {i}: {q}\n{ask(q)}\n")
