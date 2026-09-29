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
---

# Task 2 — Action Selection

## Objective

This task implements the action selection capability of the ReAct pattern.

The action selector decides what the agent should do next based on the current `ReactState`.

The implementation supports two actions:

- `lookup`
- `final_answer`

If the agent has no observations yet, it selects `lookup`.

If an observation is already available, it selects `final_answer`.

## Implementation

Supported actions are defined using:

```python
ALLOWED_ACTIONS = {"lookup", "final_answer"}
```

The `select_action()` function checks the current ReAct state and selects the next action.

If no observation is available:

```python
action = "lookup"
args = {"query": state.question}
```

If an observation is already present:

```python
action = "final_answer"
args = {"answer": f"Answer based on observation: {state.observations[-1]}"}
```

The selected action and arguments are validated before they are returned.

## Action Validation

The `validate_action()` function checks:

- Whether the action is supported
- Whether the required arguments are present
- Whether the argument values are valid

## Happy Path

For the initial state:

```text
Question: What is the status of order A100?
Observations: []
```

the selected action is:

```text
lookup
```

with arguments:

```python
{"query": "What is the status of order A100?"}
```

After adding an observation:

```text
Order A100 is packed.
```

the next selected action becomes:

```text
final_answer
```

This demonstrates the ReAct flow from action selection to the final-answer route.

## Failure Path

The implementation demonstrates rejection of an unsupported action.

It also demonstrates invalid arguments such as:

```python
{"query": ""}
```

A completed or stopped ReAct state is also prevented from selecting another action.

## Guardrails

The following guardrails are demonstrated in this task:

- **Validation:** Only supported actions and valid arguments are accepted.
- **Failure handling:** Invalid actions and arguments raise controlled errors.
- **State boundary:** Actions cannot be selected after the state has completed or stopped.
- **Traceability:** The selected action and its arguments are printed as observable evidence.
- **Secret hygiene:** No credentials or secrets are stored in source code.

## Run the Program

From the project root:

```bash
python action_selection.py
```

## Run Automated Tests

```bash
pytest tests/test_action_selection.py -v
```