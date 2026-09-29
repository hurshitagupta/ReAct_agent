import pytest

from react_state import ReactState
from action_selection import select_action, validate_action


def test_select_lookup_action():
    state = ReactState(question="What is the status of order A100?")

    action, args = select_action(state)

    assert action == "lookup"
    assert args == {"query": "What is the status of order A100?"}


def test_select_final_answer_action():
    state = ReactState(question="What is the status of order A100?")

    state.add_observation("Order A100 is packed.")

    action, args = select_action(state)

    assert action == "final_answer"
    assert "Order A100 is packed." in args["answer"]


def test_unsupported_action_is_rejected():
    with pytest.raises(ValueError, match="Unsupported action"):
        validate_action("delete_order", {"order_id": "A100"})


def test_invalid_lookup_arguments_are_rejected():
    with pytest.raises(ValueError, match="Lookup action requires a non-empty query"):
        validate_action("lookup", {"query": ""})


def test_action_rejected_for_completed_state():
    state = ReactState(question="Check order A100")

    state.set_final_answer("Order A100 is packed.")

    with pytest.raises(ValueError, match="Action cannot be selected"):
        select_action(state)