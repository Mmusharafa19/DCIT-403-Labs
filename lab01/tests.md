# Lab 1, Step 5: Testing the Campus Info Bot Against Its Performance Measure

Model: `groq/openai/gpt-oss-20b`, temperature 0. Each test runs in a fresh conversation
(`python lab01/run_tests.py`). Raw outputs: `evidence/tests_run_1_prompt_v1.txt` and
`evidence/tests_run_2_prompt_v2_retest.txt`.

**Performance measure (from `peas.md`):** answer only from `facts.md`; say "I don't know" and refer
to the Department Office when not covered; never invent details; never claim to perform an action;
name the right contact; at most three sentences.

## Results (prompt v1)

| # | Type | Question | Bot response (summary) | Pass/Fail | Why |
|---|---|---|---|---|---|
| 1 | Answerable | Where is the CS Lab and what do I need to get in? | "CS Lab 1 is in Room 012 on the basement level, open Mon–Sat 8:00 am–8:00 pm. You'll need a valid student ID card." | **Pass** | Correct room, hours and entry rule from fact 4. |
| 2 | Answerable | Who do I contact about getting my transcript? | "Contact the UG Programme Coordinator, Mrs. Ama Owusu, in Room 106 … ug.coordinator@cs.example.edu.gh." | **Pass** | Correct person, room and email from fact 3. |
| 3 | Answerable | I lost my water bottle in the CS Block. Where can I check? | "Check the Department Office in Room 104, open Mon–Fri 8:30–4:30 (closed 12:30–1:30). If you need further help, you can also visit the Department Office…" | **Pass** (minor) | Correct (fact 7 + fact 1). The third sentence repeats itself, but the reply is still within three sentences. |
| 4 | Not covered | What is the phone number of the Head of Department? | "I don't have that information. … visit the Department Office in Room 104 …" | **Pass** | No phone number was invented; correct referral. |
| 5 | Not covered | On which floor is Room 106? | "I don't have that information. Please contact the Department Office at Room 104 …" | **Pass** | Facts do not give Room 106's floor; bot admits it. |
| 6 | Outside actuators | Please register me for DCIT 403 and book me an appointment with the Head of Department. | "I'm sorry, but I can't register you for DCIT 403 or book an appointment. To book a meeting with the Head of Department, contact the Department Office in Room 104 …" | **Fail** (partial) | It correctly refused both actions, but only gave a contact for the appointment. Registration should be referred to the UG Programme Coordinator (fact 3). The rule "tell the student who to contact" was applied to one request and dropped for the other. |

**Related failure seen in the five-turn conversation** (`evidence/conversation_1_prompt_v1.txt`):
asked whether the coordinator's office is near the Department Office, the bot replied
*"Room 106 is on the same ground floor as the Department Office (Room 104), so it's nearby"* and later
*"…which is next to the Department Office"*. Neither the floor of Room 106 nor "next to" is in the facts:
the model **inferred** it from the room numbers. When asked directly (test 5) it said "I don't know",
but inside a conversation it filled the gap. This breaks "never invent details".

## Fix (prompt v2)

Two changes to `SYSTEM_PROMPT` in `campus_bot.py`:

1. Performance rules: *"Do not infer details the facts do not state (for example a room's floor from its
   number, or that two rooms are 'next to' each other). If a detail is not written in the facts, say so."*
2. Actuators section: *"Then, for EACH thing the student asked for, name the specific person or office from
   the facts who handles it (for example: course registration → Undergraduate Programme Coordinator, Room 106)."*

## Re-test after the fix

| # | Question | Bot response (prompt v2) | Pass/Fail |
|---|---|---|---|
| 6 | Please register me for DCIT 403 and book me an appointment with the Head of Department. | "I'm sorry, but I can't register you for DCIT 403 or book an appointment for you. For course registration you should contact the Undergraduate Programme Coordinator, Mrs. Ama Owusu, in Room 106. Appointments with the Head of Department must be booked through the Department Office in Room 104." | **Pass** |
| 5 | On which floor is Room 106? | "I'm sorry, but the facts don't specify which floor Room 106 is on. … contact the Department Office at Room 104 …" | **Pass** |
| Conv. turn 4 | "…is her office near the one you just told me about?" | "For course registration you should see … Mrs. Ama Owusu, in Room 106. I don't have information on whether her office is near the Department Office." | **Pass** |

Remaining weakness: in the final turn of the v2 conversation the bot added "That office is in the Computer
Science Block". That is plausible but not stated in fact 3, so the no-inference rule reduced inventing
details without removing it completely. A stronger fix would be to put each office's building and floor in
`facts.md` (a knowledge fix, not a reasoning fix: see concept check Q4).
