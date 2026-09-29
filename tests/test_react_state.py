import pytest

from react_state import ReactState, MAX_STEPS

def test_react_state_success():
    state = ReactState(question="What is the status of order A100?")

    state.increment_step()
    state.add_observation("Order A100 is packed.")
    state.set_final_answer("Order A100 is packed.")

    assert state.question == "What is the status of order A100?"
    assert state.step == 1
    assert state.observations == ["Order A100 is packed."]
    assert state.final_answer == "Order A100 is packed."
    assert state.status == "completed"


def test_empty_question_is_rejected():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        ReactState(question="")


def test_empty_observation_is_rejected():
    state = ReactState(question="Check order A100")

    with pytest.raises(ValueError, match="Observation cannot be empty"):
        state.add_observation("")


def test_step_limit():
    state = ReactState(question="Check order A100")

    for _ in range(MAX_STEPS):
        state.increment_step()

    with pytest.raises(RuntimeError, match="Maximum ReAct step limit reached"):
        state.increment_step()

    assert state.status == "stopped"