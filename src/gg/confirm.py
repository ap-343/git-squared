from contextlib import contextmanager
from rich.prompt import Prompt


@contextmanager
def confirm(prompt: str, _skip: bool = False):
    """Ask the user for a yes/no confirmation."""
    if _skip:
        yield "y"
        return

    response = Prompt.ask(f"{prompt} (y/n): ").strip().lower()
    if response in ("y", "yes"):
        yield "y"
    else:
        yield "n"
