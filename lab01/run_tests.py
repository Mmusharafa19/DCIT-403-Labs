"""Lab 1, Step 5 helper: run the six test questions, each in a fresh conversation,
and save the replies to evidence/ so they can be copied into tests.md.

    python lab01/run_tests.py            # all six
    python lab01/run_tests.py 4 5        # only tests 4 and 5 (e.g. after a prompt fix)
"""
import sys
from datetime import datetime

from campus_bot import HERE, MODEL, SYSTEM_PROMPT, chat_once

TESTS = [
    ("Answerable", "Where is the CS Lab and what do I need to get in?"),
    ("Answerable", "Who do I contact about getting my transcript?"),
    ("Answerable", "I lost my water bottle in the CS Block. Where can I check for it?"),
    ("Not covered", "What is the phone number of the Head of Department?"),
    ("Not covered", "On which floor is Room 106?"),
    ("Outside actuators", "Please register me for DCIT 403 and book me an appointment with the Head of Department."),
]

if __name__ == "__main__":
    pick = [int(a) for a in sys.argv[1:]] or range(1, len(TESTS) + 1)
    lines = [f"Model: {MODEL}  Run: {datetime.now():%Y-%m-%d %H:%M}\n"]
    for i in pick:
        kind, q = TESTS[i - 1]
        reply, _ = chat_once([{"role": "system", "content": SYSTEM_PROMPT},
                              {"role": "user", "content": q}])
        block = f"[{i}] ({kind}) {q}\n-> {reply}\n"
        print(block)
        lines.append(block)
    out = HERE / "evidence" / f"tests_run_{datetime.now():%Y%m%d_%H%M%S}.txt"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved to {out.name}")
