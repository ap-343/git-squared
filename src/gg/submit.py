from .branch import Branch, checked_out
from .log import log
from .repo import repo
from .pr import create_pr


def submit(_force: bool = False, **kwargs):
    r = repo()
    if _force:
        r.git.push("origin", "HEAD", force=True)
    else:
        r.git.push("origin", "HEAD", force_with_lease=True)
    log(
        f"Submitted [bold]{Branch.active().name}[bold]",
        _type="success",
        _emoji=":ship:",
    )
    if Branch.active().name != r.main().name:
        create_pr(**kwargs)


def checkout_and_submit(branch: Branch, _force: bool = False, **kwargs):
    with checked_out(branch):
        submit(_force=_force, **kwargs)
