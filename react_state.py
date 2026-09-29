from dataclasses import dataclass, field
from typing import Optional

MAX_STEPS = 3

@dataclass
class ReactState:
    question: str
    step: int = 0
    observations: list[str] = field(default_factory=list)
    final_answer: Optional[str] = None
    status: str = "running"

    def __post_init__(self):
        self.question = self.question.strip()

        if not self.question:
            raise ValueError("Question cannot be empty.")

        if self.step < 0:
            raise ValueError("Step cannot be negative.")

        if self.step > MAX_STEPS:
            raise ValueError(f"Step cannot exceed maximum limit of {MAX_STEPS}.")

    def add_observation(self, observation: str) -> None:
        observation = observation.strip()

        if not observation:
            raise ValueError("Observation cannot be empty.")

        self.observations.append(observation)

    def increment_step(self) -> None:
        if self.step >= MAX_STEPS:
            self.status = "stopped"
            raise RuntimeError("Maximum ReAct step limit reached.")

        self.step += 1

    def set_final_answer(self, answer: str) -> None:
        answer = answer.strip()

        if not answer:
            raise ValueError("Final answer cannot be empty.")

        self.final_answer = answer
        self.status = "completed"


def main():
    print("=== ReAct State Demo ===")

    print("\nHappy Path:")

    state = ReactState(question="What is the status of order A100?")

    print("Initial state:")
    print(state)

    state.increment_step()
    state.add_observation("Order A100 is packed.")

    print("\nState after observation:")
    print(state)

    state.set_final_answer("Order A100 is packed.")

    print("\nFinal state:")
    print(state)

    print("\nFailure Path:")

    try:
        invalid_state = ReactState(question="")
        print(invalid_state)

    except ValueError as error:
        print(f"Rejected: {error}")

    print("\nStep Limit Demonstration:")

    limited_state = ReactState(question="Check order B200")

    try:
        limited_state.increment_step()
        limited_state.increment_step()
        limited_state.increment_step()
        limited_state.increment_step()

    except RuntimeError as error:
        print(f"Stopped: {error}")
        print(f"Status: {limited_state.status}")


if __name__ == "__main__":
    main()