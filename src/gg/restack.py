from .branch import checked_out
from .repo import repo
from .log import log


def restack(branch, _log=True):
    with checked_out(branch, _log=False) as (co, og):
        if co.tracking_branch():
            if co.commits_behind() > 0:
                repo().git.rebase()
                if _log:
                    log(f"🥞 Restacked {co.name}")
            else:
                log(f"Already up to date: {co.name}", _type="dim")
