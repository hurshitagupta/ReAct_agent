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

---

# Task 3 — Observation

## Objective

This task implements observation handling in the ReAct control pattern.

The observation component executes a tool, validates its result, and stores the result inside `ReactState`.

It also ensures that tool failures are converted into observations instead of immediately crashing the ReAct flow.

## Implementation

The main function is:

```python
execute_observation()
```

It receives:

- Current `ReactState`
- Tool function
- Tool arguments

The tool is executed and its returned value is validated before being stored as an observation.

Example:

```python
execute_observation(state, lookup_tool, {"query": state.question})
```

## Observation Validation

The `validate_observation()` function ensures that every observation:

- Is a string
- Is not empty

Invalid tool results are rejected and converted into failure observations.

## Happy Path

For:

```text
What is the status of order A100?
```

the lookup tool returns:

```text
Order A100 is packed.
```

The state is updated to contain:

```text
step = 1
observations = ["Order A100 is packed."]
```

This demonstrates successful observation handling.

## Failure Handling

The assessment requires a tool failure to become an observation.

For example, if the lookup tool receives an empty query:

```python
{"query": ""}
```

the tool raises an error.

Instead of stopping the whole program, the error is converted into:

```text
Tool failure: Lookup query is required.
```

This message is stored in the ReAct state as an observation.

This allows later steps in the ReAct loop to inspect the failure and either recover or stop transparently.

## Retry Handling

Transient failures are represented using:

```python
TransientToolError
```

Only this type of failure is retried.

The retry limit is:

```python
MAX_RETRIES = 2
```

For example, if a tool temporarily fails on the first attempt and succeeds on the second attempt, the output shows:

```text
Attempt 1: transient failure
Attempt 2: success
```

Permanent validation errors are not retried.

## Timeout Handling

Tool execution is wrapped with a timeout using:

```python
ThreadPoolExecutor
```

The configured timeout is:

```python
TOOL_TIMEOUT = 1.0
```

If a tool takes longer than the allowed timeout, the failure becomes an observation:

```text
Tool failure: Tool execution timed out.
```

## Guardrails

The following guardrails are demonstrated in this task:

- **Step limit:** Reuses the maximum step limit from `ReactState`.
- **Timeout:** Tool calls use a fixed timeout.
- **Retry:** Only transient failures are retried with a capped retry count.
- **Validation:** Tool arguments and observations are validated.
- **Failure handling:** Tool failures are stored as observations.
- **Traceability:** Attempts, failures, and observations are printed.
- **Secret hygiene:** No credentials or secrets are stored in source code.

## Run the Program

From the project root:

```bash
python observation.py
```

## Run Automated Tests

```bash
pytest tests/test_observation.py -v
```

---

# Task 4 — Termination

## Objective

This task implements the termination capability of the ReAct control pattern.

The termination logic decides whether the ReAct loop should:

- Continue execution
- Stop because a final answer is available
- Stop because the maximum step limit has been reached
- Stop because the state is already marked as stopped

This task reuses the `ReactState` and `MAX_STEPS` values implemented in Task 1.

## Implementation

The main termination check is implemented using:

```python
should_terminate(state)
```

This function checks the current ReAct state and returns:

```python
(True, reason)
```

when execution should stop, or:

```python
(False, "continue")
```

when the ReAct loop can continue.

## Final Answer Route

The assessment requires ReAct to have an explicit final-answer route.

This is implemented using:

```python
terminate_with_answer()
```

The function stores the final answer in the state and changes the state status to:

```text
completed
```

After this, the termination check returns:

```text
Terminate: True
Reason: final_answer
```

## Step Limit Termination

The maximum number of ReAct steps is defined in Task 1 using:

```python
MAX_STEPS = 3
```

If the current step reaches this limit, `should_terminate()` stops the ReAct process.

This prevents the ReAct loop from continuing indefinitely.

## Continue Route

If there is no final answer and the maximum step limit has not been reached, the function returns:

```text
Terminate: False
Reason: continue
```

This tells the ReAct loop that another action can be performed.

## Failure Path

The implementation rejects an empty final answer.

It also prevents a completed or stopped state from receiving another final answer.

## Guardrails

The following guardrails are demonstrated in this task:

- **Step limit:** Execution stops when `MAX_STEPS` is reached.
- **Validation:** Final answers must contain valid non-empty text.
- **Failure handling:** Invalid termination attempts raise controlled errors.
- **State boundary:** Completed or stopped states cannot receive another final answer.
- **Traceability:** Termination returns a clear reason such as `final_answer`, `step_limit`, or `continue`.
- **Secret hygiene:** No credentials or secrets are stored in source code.

## Run the Program

From the project root:

```bash
python termination.py
```

## Run Automated Tests

```bash
pytest tests/test_termination.py -v
```