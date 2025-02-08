from .branch import Branch, checked_out
from .log import log
from .repo import repo
from .pr import create_pr


def submit(_force: bool = False):
    if _force:
        repo().git.push("origin", "HEAD", force=True)
    else:
        repo().git.push("origin", "HEAD", force_with_lease=True)
    log(
        f"Submitted [bold]{Branch.active().name}[bold]",
        _type="success",
        _emoji=":ship:",
    )
    create_pr()


def checkout_and_submit(branch: Branch, _force: bool = False, **kwargs):
    with checked_out(branch):
        submit(_force=_force, **kwargs)
