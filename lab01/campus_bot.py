"""Lab 1, Step 4: Campus Info Bot.

A terminal chat loop. The whole conversation history (the percept sequence)
is sent to the model every turn. Facts live in facts.md so they can change
without touching the code. Type 'quit' to exit.

    python lab01/campus_bot.py
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from litellm import completion

HERE = Path(__file__).resolve().parent
# Fix for a real crash on Windows: the model sometimes replies with characters such as
# a narrow no-break space (U+202F, e.g. "8:30 am") that the cp1252 console cannot print.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv()
MODEL = os.getenv("LLM_MODEL")

FACTS = (HERE / "facts.md").read_text(encoding="utf-8")

# The system prompt is built section by section from peas.md.
SYSTEM_PROMPT = f"""You are the Campus Info Bot for the Department of Computer Science.
You help students find offices, opening hours and the right person to contact.

## Performance measure (rules you must follow)
- Answer ONLY from the FACTS below. Never invent names, room numbers, times, emails or phone numbers.
- Do not infer details the facts do not state (for example a room's floor from its number, or
  that two rooms are "next to" each other). If a detail is not written in the facts, say so.
- If the facts do not cover the question, say you do not have that information and refer the
  student to the Department Office (Room 104, Mon-Fri 8:30 am-4:30 pm, closed 12:30-1:30 pm).
- Use what the student said earlier in this conversation (for example their name, or the office
  they asked about) so they do not have to repeat themselves.
- Keep replies short: at most three sentences.

## Environment (facts you know)
<facts>
{FACTS}
</facts>

## Actuators (what you can and cannot do)
- You can ONLY reply with text.
- You cannot register students, book appointments, send emails, submit forms or change any record.
  If asked to do any of these, say clearly that you cannot do it yourself. Then, for EACH thing
  the student asked for, name the specific person or office from the facts who handles it
  (for example: course registration -> Undergraduate Programme Coordinator, Room 106).
  Never pretend that an action has been done.
"""


def chat_once(history: list[dict]) -> tuple[str, float]:
    start = time.perf_counter()
    resp = completion(model=MODEL, messages=history, temperature=0)
    return resp.choices[0].message.content.strip(), time.perf_counter() - start


def main():
    if not MODEL:
        print("LLM_MODEL is not set. Copy .env.example to .env and set LLM_MODEL.")
        return
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    transcript = []
    print("Campus Info Bot (type 'quit' to exit)")
    while True:
        try:
            user = input("You: ").strip()
        except EOFError:
            break
        if not user:
            continue
        if user.lower() == "quit":
            break
        history.append({"role": "user", "content": user})
        reply, secs = chat_once(history)
        history.append({"role": "assistant", "content": reply})
        print(f"Bot: {reply}  ({secs:.2f}s)")
        transcript.append(f"You: {user}\nBot: {reply}\n")

    if transcript:
        out = HERE / "evidence" / f"conversation_{datetime.now():%Y%m%d_%H%M%S}.txt"
        out.write_text(f"Model: {MODEL}\n\n" + "\n".join(transcript), encoding="utf-8")
        print(f"Transcript saved to {out.relative_to(HERE.parent)}")


if __name__ == "__main__":
    main()
