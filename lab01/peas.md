# Lab 1, Step 3: PEAS Analysis of the Campus Info Bot

## PEAS table

| PEAS | Campus Info Bot |
|---|---|
| **Performance** | Correct answers about office locations, opening hours and who to contact, taken only from the facts block; says "I don't know" and refers the student to the Department Office (Room 104) when a question is not covered; never invents names, rooms or times; never claims to have registered, booked or changed anything; short replies (at most 3 sentences); remembers what the student said earlier in the conversation. |
| **Environment** | New and continuing students chatting in a terminal; the department's office facts (`facts.md`); the Department Office as the human fallback. |
| **Actuators** | Send a text reply (answer, clarifying question, or referral to the Department Office). It cannot register, book, email or change any record. |
| **Sensors** | The student's typed messages; the conversation history (all earlier turns); the facts block loaded from `facts.md`. |

## Environment properties

| Property | Classification | Justification |
|---|---|---|
| Observable | **Partially observable** | The bot sees only what the student types; it cannot see the student's identity, records, location or what they really mean. |
| Deterministic / stochastic | **Stochastic** | Students phrase questions unpredictably, and the model's reply to the same input can vary. |
| Episodic / sequential | **Sequential** | Earlier turns matter: "what time does *it* open?" only makes sense given the office mentioned before. |
| Static / dynamic | **Static** (during a chat) | The facts do not change while the student is typing; the bot waits for each message. (Across a semester the facts do change, which is why they live in `facts.md`.) |
| Discrete / continuous | **Discrete** | Interaction happens in distinct turns of text with a finite set of facts. |
| Single / multi-agent | **Single-agent** (cooperative user) | The student is a cooperative user, not an opponent; the bot does not compete or negotiate with other agents. A user trying to make the bot misbehave would make it partly multi-agent. |
