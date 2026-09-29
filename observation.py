import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Callable, Any

from react_state import ReactState

MAX_RETRIES = 2
TOOL_TIMEOUT = 1.0

class TransientToolError(Exception):
    """Error that may succeed if the tool is retried."""
    pass

def validate_observation(observation: Any) -> str:
    if not isinstance(observation, str):
        raise ValueError("Tool observation must be a string.")

    observation = observation.strip()

    if not observation:
        raise ValueError("Tool observation cannot be empty.")

    return observation

def call_with_timeout(tool: Callable[[dict], str], args: dict, timeout: float) -> str:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(tool, args)

        try:
            return future.result(timeout=timeout)

        except TimeoutError:
            raise TimeoutError("Tool execution timed out.")

def execute_observation(state: ReactState, tool: Callable[[dict], str], args: dict) -> str:

    if state.status != "running":
        raise ValueError("Observation cannot be recorded for a completed or stopped state.")

    if not isinstance(args, dict):
        raise ValueError("Tool arguments must be a dictionary.")

    attempts = 0

    while attempts <= MAX_RETRIES:
        attempts += 1

        try:
            result = call_with_timeout(tool, args, TOOL_TIMEOUT)

            observation = validate_observation(result)

            state.increment_step()
            state.add_observation(observation)

            print(f"Attempt {attempts}: success")
            print(f"Observation: {observation}")

            return observation

        except TransientToolError as error:
            print(f"Attempt {attempts}: transient failure - {error}")

            if attempts > MAX_RETRIES:
                observation = f"Tool failed after {attempts} attempts: {error}"

                state.increment_step()
                state.add_observation(observation)

                return observation

            time.sleep(0.1)

        except TimeoutError as error:
            observation = f"Tool failure: {error}"

            state.increment_step()
            state.add_observation(observation)

            print(observation)

            return observation

        except (ValueError, TypeError) as error:
            observation = f"Tool failure: {error}"

            state.increment_step()
            state.add_observation(observation)

            print(observation)

            return observation

def lookup_tool(args: dict) -> str:
    query = args.get("query")

    if not query:
        raise ValueError("Lookup query is required.")

    if "A100" in query:
        return "Order A100 is packed."

    return "Order not found."


def main():
    print("=== Observation Demo ===")

    print("\nHappy Path")

    state = ReactState(question="What is the status of order A100?")

    execute_observation(state, lookup_tool, {"query": state.question})

    print(f"Stored observations: {state.observations}")
    print(f"Current step: {state.step}")

    print("\nFailure Path")

    failure_state = ReactState(question="Check order")

    execute_observation(failure_state, lookup_tool, {"query": ""})

    print(f"Stored observations: {failure_state.observations}")

    print("\nRetry Demonstration")

    retry_state = ReactState(question="Check order A100")

    attempt_counter = {"count": 0}

    def temporary_failure_tool(args):
        attempt_counter["count"] += 1

        if attempt_counter["count"] == 1:
            raise TransientToolError("Temporary service failure")

        return "Order A100 is packed."

    execute_observation(retry_state, temporary_failure_tool, {"query": retry_state.question})

    print(f"Stored observations: {retry_state.observations}")


if __name__ == "__main__":
    main()