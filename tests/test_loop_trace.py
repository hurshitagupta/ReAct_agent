from loop_trace import run_react, lookup_tool

def test_react_loop_success():
    tools = {"lookup": lookup_tool}

    answer, trace = run_react("What is the status of order A100?", tools)

    assert "Order A100 is packed." in answer
    assert len(trace) == 2
    assert trace[0]["action"] == "lookup"
    assert trace[0]["observation"] == "Order A100 is packed."
    assert trace[1]["action"] == "final_answer"
    assert trace[1]["status"] == "completed"

def test_trace_contains_required_information():
    tools = {"lookup": lookup_tool}

    answer, trace = run_react("What is the status of order A100?", tools)

    first_step = trace[0]

    assert "step" in first_step
    assert "action" in first_step
    assert "arguments" in first_step
    assert "observation" in first_step
    assert "status" in first_step


def test_missing_tool_stops_at_step_limit():
    answer, trace = run_react("What is the status of order A100?", {})

    assert answer == "Stopped: step_limit"

    assert len(trace) == 3

    assert all(
        entry["status"] == "tool_not_found" 
        for entry in trace)

    assert all(
        "Tool failure" in entry["observation"] 
        for entry in trace)

def test_unknown_order_still_returns_final_answer():
    tools = {"lookup": lookup_tool}

    answer, trace = run_react("What is the status of order Z999?",tools)

    assert "Order not found." in answer
    assert trace[0]["observation"] == "Order not found."