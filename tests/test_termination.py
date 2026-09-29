import pytest

from react_state import ReactState, MAX_STEPS
from termination import should_terminate, terminate_with_answer

def test_final_answer_terminates():
    state = ReactState(question="What is the status of order A100?")

    state.add_observation("Order A100 is packed.")

    answer = terminate_with_answer(state, "Order A100 is packed.")

    terminate, reason = should_terminate(state)

    assert answer == "Order A100 is packed."
    assert terminate is True
    assert reason == "final_answer"
    assert state.status == "completed"

def test_running_state_continues():
    state = ReactState(question="Check order A100")

    terminate, reason = should_terminate(state)

    assert terminate is False
    assert reason == "continue"
    assert state.status == "running"


def test_step_limit_terminates():
    state = ReactState(question="Check order A100")

    for _ in range(MAX_STEPS):
        state.increment_step()

    terminate, reason = should_terminate(state)

    assert terminate is True
    assert reason == "step_limit"
    assert state.status == "stopped"

def test_empty_final_answer_is_rejected():
    state = ReactState(question="Check order A100")

    with pytest.raises(ValueError, match="Final answer cannot be empty"):
        terminate_with_answer(state, "")


def test_completed_state_cannot_receive_new_answer():
    state = ReactState(question="Check order A100")

    terminate_with_answer( state, "Order A100 is packed.")

    with pytest.raises(ValueError, match="Cannot set final answer"):
        terminate_with_answer(state, "Another answer")