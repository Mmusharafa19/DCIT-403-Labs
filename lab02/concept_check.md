# Lab 2: Architectures: A ReAct Agent From Scratch: Concept Check

Answer in your own words before the Wednesday session (independent work). Your answers feed Section 2 of your lab report (Concept and classical root).

## Q1. Classify a thermostat, a chess engine and a ReAct agent as reactive, deliberative or hybrid, with one reason each.

_Your answer:_

- **Thermostat: reactive.** It applies a fixed condition-action rule to the current reading ("if temperature < setpoint, turn heating on") with no plan and no memory of the past.
- **Chess engine: deliberative.** It keeps an internal model of the board and searches many moves ahead to build a plan before choosing a move.
- **ReAct agent: hybrid.** Each Thought is deliberation (it plans what to compute or look up next), but each step also reacts to the latest Observation and can change course immediately.

## Q2. In the trace above, which lines are percepts, and which are actions?

_Your answer:_

- **Percepts:** the user's question, and the two `Observation:` lines (`Observation: 1025` and `Observation: 175`). These come from outside the model.
- **Actions:** each `Action` + `Action Input` pair: `calculator / 4*185 + 3*95`, `calculator / 1200 - 1025`, and `finish / You will have GHS 175 left.`
- The `Thought:` lines are neither: they are internal deliberation (the reasoning that chooses the action).

## Q3. Why do we pass `stop=["Observation:"]` when calling the model?

_Your answer:_

So the model stops generating as soon as it has chosen an action. Without it, the model would keep writing and invent its own `Observation:` (for example guessing a calculator result or a Wikipedia fact), and then continue reasoning on that made-up percept. The stop sequence forces control back to our code, which runs the real tool and supplies the real observation. In agent terms: percepts must come from the environment, not be hallucinated by the decision-maker.

## Q4. Map the trace above to the BDI terms belief, desire and intention.

_Your answer:_

- **Belief:** what the agent holds true so far: the question's facts (budget GHS 1,200; 4 bags of rice at 185; 3 gallons of oil at 95) plus each observation (total cost = 1025, remainder = 175).
- **Desire:** the goal: tell the trader how much money will be left.
- **Intention:** the plan the agent commits to in its Thoughts: "compute the total cost first, then subtract it from the budget". Each `Action` is one step of executing that intention; after `Observation: 1025` the belief is updated and the agent moves on to the next step of the plan (the BDI cycle: perceive, update beliefs, act on intention, repeat).
