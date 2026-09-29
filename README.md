# Task 1 — ReAct State

## Objective

This task implements the state used by the ReAct control loop.

The state keeps track of:

- User question
- Current step number
- Tool observations
- Final answer
- Current execution status

The state is designed so that later ReAct components such as action selection, observation handling, termination, and loop tracing can use the same shared structure.

## Implementation

The `ReactState` dataclass contains the main information required during a ReAct run.

```python
@dataclass
class ReactState:
    question: str
    step: int = 0
    observations: list[str] = field(default_factory=list)
    final_answer: Optional[str] = None
    status: str = "running"
```

The implementation includes methods to:

- Add observations
- Increment the current ReAct step
- Store the final answer
- Update the execution status

Input validation is performed using `__post_init__()` after the dataclass creates the object.

The implementation rejects:

- Empty questions
- Empty observations
- Empty final answers
- Invalid step values

A maximum step limit is also applied:

```python
MAX_STEPS = 3
```

If the agent tries to exceed this limit, execution is stopped.

## Happy Path

The demonstration creates a valid ReAct state for:

```text
What is the status of order A100?
```

The state is updated with the observation:

```text
Order A100 is packed.
```

The final answer is then stored and the state becomes:

```text
status = completed
```

## Failure Path

An empty question is rejected with a `ValueError`.

Example:

```text
Rejected: Question cannot be empty.
```

The implementation also demonstrates the maximum-step boundary. If the number of allowed steps is exceeded, execution stops with:

```text
Maximum ReAct step limit reached.
```

## Guardrails

The following guardrails are demonstrated in this task:

- **Step limit:** Maximum of 3 ReAct steps.
- **Validation:** Questions, observations, answers, and step values are validated.
- **Failure handling:** Invalid state values raise controlled exceptions.
- **Traceability:** The complete `ReactState` can be printed and inspected.
- **Secret hygiene:** No credentials or secrets are stored in the source code.

## Run the Program

From the project root:

```bash
python react_state.py
```

## Run Automated Tests

```bash
pytest tests/test_react_state.py -v
```
