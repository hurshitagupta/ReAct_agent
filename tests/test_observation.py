import time

from react_state import ReactState
from observation import execute_observation, lookup_tool, TransientToolError

def test_successful_observation():
    state = ReactState(question="What is the status of order A100?")

    observation = execute_observation(state,lookup_tool,{"query": state.question})

    assert observation == "Order A100 is packed."
    assert state.observations == ["Order A100 is packed."]
    assert state.step == 1

def test_tool_failure_becomes_observation():
    state = ReactState(question="Check order")

    observation = execute_observation(state, lookup_tool, {"query": ""})

    assert "Tool failure" in observation
    assert "Lookup query is required" in observation

    assert observation in state.observations

def test_transient_failure_is_retried():
    state = ReactState(question="Check order A100")

    counter = {"count": 0}

    def temporary_tool(args):
        counter["count"] += 1

        if counter["count"] == 1:
            raise TransientToolError("Temporary failure")

        return "Order A100 is packed."

    observation = execute_observation(state, temporary_tool, {"query": state.question})

    assert observation == "Order A100 is packed."
    assert counter["count"] == 2

def test_tool_timeout_becomes_observation():
    state = ReactState(question="Check order A100")

    def slow_tool(args):
        time.sleep(1.5)
        return "Order A100 is packed."

    observation = execute_observation(state, slow_tool, {"query": state.question})

    assert "timed out" in observation
    assert observation in state.observations

def test_invalid_arguments_are_rejected():
    state = ReactState(question="Check order A100")

    try:
        execute_observation(state,lookup_tool,"invalid arguments")

        assert False

    except ValueError as error:
        assert "dictionary" in str(error)