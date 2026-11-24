# Lab 1: Agents Then and Now: PEAS and Your First LLM Call: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Give the PEAS description of a self-checkout machine at a supermarket.

_Your answer:_

- **Performance:** every item scanned and charged at the correct price; correct total and change/payment; short checkout time; low rate of theft and missed items; calls staff for age-restricted items or errors.
- **Environment:** the checkout station (scanner, bagging area scale, payment terminal), shoppers, their items, the store's price database, and the supervising staff member.
- **Actuators:** the screen and speaker (prompts and messages), the receipt printer, the cash/change dispenser, the payment terminal request, and the "call assistant" light/alert.
- **Sensors:** barcode scanner, bagging-area weight scale, touchscreen input, card reader/cash acceptor, and in some machines a camera.

## Q2. Is the Campus Info Bot's environment episodic or sequential? Justify your answer using what the bot needs to remember.

_Your answer:_

Sequential. What the bot should say depends on earlier turns: if a student first asks "Where is the Department Office?" and then "What time does it close?", the bot must remember that "it" means the Department Office. It may also need to remember the student's name or what they already asked so they don't repeat themselves. In an episodic environment each question would be judged on its own, with no need for history.

## Q3. Which part of an LLM agent plays the role of the percept sequence?

_Your answer:_

The `messages` list that is sent to the model on every turn: the system prompt plus every user message and assistant reply so far (and, from Lab 2, tool observations). The model itself has no memory between calls, so this list *is* everything the agent has perceived.

## Q4. An agent gives a wrong office location because its facts block was out of date. Was it irrational? Explain.

_Your answer:_

No. Rationality means choosing the action that is expected to maximise the performance measure *given the percept sequence and built-in knowledge*. If the agent faithfully answered from the facts it was given, it acted rationally; the error came from wrong built-in knowledge, not from bad decision-making. Rational is not the same as omniscient. The fix is in the environment/knowledge (update `facts.md`), not in the agent's reasoning. It would only be irrational if the facts were correct and the agent ignored them or made something up.
