from react_state import ReactState, MAX_STEPS

def should_terminate(state: ReactState) -> tuple[bool, str]:
    if state.final_answer:
        return True, "final_answer"

    if state.step >= MAX_STEPS:
        state.status = "stopped"
        return True, "step_limit"

    if state.status == "stopped":
        return True, "stopped"

    return False, "continue"


def terminate_with_answer(state: ReactState, answer: str) -> str:
    if state.status != "running":
        raise ValueError("Cannot set final answer for a completed or stopped state.")

    state.set_final_answer(answer)

    return state.final_answer

def main():
    print("=== Termination Demo ===")
    print("\nHappy Path: Final Answer")

    state = ReactState(question="What is the status of order A100?")

    state.add_observation("Order A100 is packed.")

    answer = terminate_with_answer(state, "Order A100 is packed.")

    terminate, reason = should_terminate(state)

    print(f"Final answer: {answer}")
    print(f"Terminate: {terminate}")
    print(f"Reason: {reason}")
    print(f"Status: {state.status}")

    print("\nStep Limit Path")

    limited_state = ReactState(question="Check order B200")

    for _ in range(MAX_STEPS):
        limited_state.increment_step()

    terminate, reason = should_terminate(limited_state)

    print(f"Terminate: {terminate}")
    print(f"Reason: {reason}")
    print(f"Status: {limited_state.status}")

    print("\nFailure Path: Invalid Final Answer")

    failure_state = ReactState(question="Check order C300")

    try:
        terminate_with_answer(failure_state, "")

    except ValueError as error:
        print(f"Rejected: {error}")

if __name__ == "__main__":
    main()