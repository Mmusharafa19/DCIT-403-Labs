"""Lab 1 diagnostic: answer the questions in questions.txt through LiteLLM.

Reads three questions from questions.txt, sends each to the model and writes the
answers plus the total tokens used to answers.md.

    python lab01/diagnostic/diag.py
"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

HERE = Path(__file__).resolve().parent
load_dotenv()
MODEL = os.getenv("LLM_MODEL")

if not MODEL:
    print("LLM_MODEL is not set. Add a line such as LLM_MODEL=groq/openai/gpt-oss-20b to your .env file.")
    sys.exit(1)

questions_file = HERE / "questions.txt"
if not questions_file.exists():
    print(f"Cannot find {questions_file.name}. Put one question per line in it.")
    sys.exit(1)

questions = [q.strip() for q in questions_file.read_text(encoding="utf-8").splitlines() if q.strip()][:3]

lines = [f"# Diagnostic answers\n\nModel: `{MODEL}`\n"]
total_tokens = 0
for i, q in enumerate(questions, 1):
    try:
        resp = completion(model=MODEL, temperature=0, messages=[
            {"role": "system", "content": "Answer briefly and clearly."},
            {"role": "user", "content": q},
        ])
        answer = resp.choices[0].message.content.strip()
        total_tokens += resp.usage.total_tokens
    except Exception as e:  # keep going if one call fails
        answer = f"Error calling the model: {e.__class__.__name__}: {str(e)[:200]}"
    lines.append(f"## Q{i}. {q}\n\n{answer}\n")
    print(f"Q{i} done")

lines.append(f"**Total tokens used:** {total_tokens}\n")
(HERE / "answers.md").write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote answers.md (total tokens: {total_tokens})")
