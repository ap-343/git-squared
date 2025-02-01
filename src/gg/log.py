from rich import print
from contextlib import contextmanager


def log(msg, _type=None, _title=None, _emoji=None, _print=True):
    if _emoji:
        msg = f"{_emoji} {msg}"
    if _title:
        msg = f"{_title}: {msg}"
    if _type == "success":
        msg = "[green]" + msg + "[/green]"
    elif _type == "error":
        msg = "[red]Error: " + msg + "[/red]"
    elif _type == "happy":
        msg = "[cyan]" + msg + "[/cyan]"
    elif _type == "warn":
        msg = "[orange3]" + msg + "[/orange3]"
    elif _type == "dim":
        msg = "[dim]" + msg + "[/dim]"
    if _print:
        print(f"{msg}")
    else:
        return msg


@contextmanager
def pad(n=1):
    for _ in range(n):
        log("")
    yield
    for _ in range(n):
        log("")
