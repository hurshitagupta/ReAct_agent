from typing import Any

from react_state import ReactState


ALLOWED_ACTIONS = {"lookup", "final_answer"}


def validate_action(action: str, args: dict[str, Any]) -> None:
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported action: {action}")

    if action == "lookup":
        query = args.get("query")

        if not isinstance(query, str) or not query.strip():
            raise ValueError("Lookup action requires a non-empty query.")

    if action == "final_answer":
        answer = args.get("answer")

        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("Final answer action requires a non-empty answer.")


def select_action(state: ReactState) -> tuple[str, dict[str, Any]]:
    if state.status != "running":
        raise ValueError("Action cannot be selected for a completed or stopped state.")

    if not state.observations:
        action = "lookup"
        args = {"query": state.question}

    elif state.observations[-1].startswith("Tool failure:"):
        action = "lookup"
        args = {"query": state.question}

    else:
        action = "final_answer"
        args = {"answer": f"Answer based on observation: {state.observations[-1]}"}

    validate_action(action, args)

    return action, args


def main():
    print("=== Action Selection Demo ===")

    print("\nHappy Path 1: Select lookup")

    state = ReactState(question="What is the status of order A100?")

    action, args = select_action(state)

    print(f"Selected action: {action}")
    print(f"Arguments: {args}")

    print("\nHappy Path 2: Select final answer")

    state.add_observation("Order A100 is packed.")

    action, args = select_action(state)

    print(f"Selected action: {action}")
    print(f"Arguments: {args}")

    print("\nFailure Path: Unsupported action")

    try:
        validate_action("delete_order", {"order_id": "A100"})

    except ValueError as error:
        print(f"Rejected: {error}")

    print("\nFailure Path: Invalid arguments")

    try:
        validate_action("lookup",{"query": ""})

    except ValueError as error:
        print(f"Rejected: {error}")


if __name__ == "__main__":
    main()