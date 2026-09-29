from typing import Callable

from react_state import ReactState
from action_selection import select_action
from observation import execute_observation
from termination import should_terminate, terminate_with_answer

def run_react(question: str, tools: dict[str, Callable]) -> tuple[str, list[dict]]:
    state = ReactState(question=question)
    trace = []

    while True:
        terminate, reason = should_terminate(state)

        if terminate:
            if state.final_answer:
                return state.final_answer, trace

            return f"Stopped: {reason}", trace

        action, args = select_action(state)

        trace_entry = {
            "step": state.step + 1,
            "action": action,
            "arguments": args,
        }

        if action == "final_answer":
            answer = args["answer"]

            terminate_with_answer(state, answer)

            trace_entry["result"] = answer
            trace_entry["status"] = state.status
            trace.append(trace_entry)

            continue

        if action not in tools:
            observation = (f"Tool failure: Action '{action}' is not available.")

            state.increment_step()
            state.add_observation(observation)
            trace_entry["observation"] = observation
            trace_entry["status"] = "tool_not_found"
            trace.append(trace_entry)

            continue

        observation = execute_observation(state,tools[action], args)

        trace_entry["observation"] = observation
        trace_entry["status"] = "observed"
        trace.append(trace_entry)


def lookup_tool(args: dict) -> str:
    query = args.get("query", "")

    if not query:
        raise ValueError("Lookup query is required.")

    if "A100" in query:
        return "Order A100 is packed."

    return "Order not found."

def print_trace(trace: list[dict]) -> None:
    for entry in trace:
        print(
            f"Step {entry['step']} | "
            f"Action: {entry['action']} | "
            f"Status: {entry['status']}")

        if "arguments" in entry:
            print(f"Arguments: {entry['arguments']}")

        if "observation" in entry:
            print(f"Observation: {entry['observation']}")

        if "result" in entry:
            print(f"Result: {entry['result']}")

def main():
    print("=== ReAct Loop Trace Demo ===")

    print("\nHappy Path")

    tools = {"lookup": lookup_tool}

    answer, trace = run_react("What is the status of order A100?", tools)

    print_trace(trace)

    print(f"\nFinal Answer: {answer}")

    print("\nFailure Path: Missing Tool")

    answer, trace = run_react("What is the status of order A100?",{})

    print_trace(trace)
    print(f"\nFinal Result: {answer}")

if __name__ == "__main__":
    main()