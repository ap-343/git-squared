#!/usr/bin/env python3
import arguably
from .log import log, pad
from .branch import Branch, create_new_branch, checked_out
from .repo import repo, not_main
from .exception import GgException
from .ls import draw_tree_2
from .tree import traverse
from .confirm import confirm
from .restack import restack as _restack
from .submit import submit as _submit, checkout_and_submit
import git
from .github import Github
import subprocess
import questionary


@arguably.command
def ls():
    """
    List all branches and current status
    """
    with pad():
        r = repo()
        draw_tree_2(r, _print=True)
        if len(r.staged() + r.unstaged() + r.untracked()):
            log("")
            if len(r.staged()):
                for f in r.staged():
                    log(f"• {f}", _type="success")
            if len(r.unstaged()):
                for f in r.unstaged():
                    log(f"◦ {f}")
            if len(r.untracked()):
                for f in r.untracked():
                    log(f"◦ {f}", _type="dim")


@arguably.command
def rm(name: str = None, *, y: bool = False):
    """
    Remove (delete) this branch or a named branch

    Args:
        name: the name of the branch to remove
        y: whether to skip confirmation
    """
    r = repo()
    current_branch = name if name else r.active_branch.name
    with confirm(
        f"Are you sure you want to delete {current_branch}?", _skip=y
    ) as answer:
        if answer == "y":
            # cant delete the branch we are on
            if current_branch == r.active_branch.name:
                Branch.active().parent().checkout(_log=False)

            with pad():
                Branch(current_branch).delete()


@arguably.command
def go(name):
    """
    Go to a branch if it exists. Otherwise, create a new branch tracking the current branch.

    Args:
        name: the name of the branch to go to
    """
    with pad():
        if not Branch(name).exists():
            create_new_branch(name)

        if Branch(name).exists():
            Branch(name).checkout(_log=True)
            r = repo()
            draw_tree_2(r, _print=True, _highlight=r.active_branch)


@arguably.command()
def down():
    """
    Move down the stack from the current branch; ie, move to the parent branch
    """
    go(Branch.active().parent().name)


@arguably.command()
def up():
    """
    Move up the stack from the current branch; ie, move to the child branch
    """
    children = Branch.active().children()
    if len(children) == 0:
        log("Cannot go up! No child branches found")
        return
    elif len(children) == 1:
        go(children[0].name)
    else:
        choice = questionary.select(
            "Select a branch:", choices=[x.name for x in children]
        ).ask()
        go(choice)


@arguably.command
def restack():
    """
    Restack this branch and all children onto its tracking branch
    """
    with pad():
        traverse(Branch.from_head(repo().active_branch), _restack)


@arguably.command
def status():
    """
    Show git status (alias for `git status`)
    """
    subprocess.run(["git", "status"])


@arguably.command
def add(*opts):
    """
    Add files to the staging area (alias for `git add`)

    Args:
        opts: the options to pass to `git add`
    """
    subprocess.run(["git", "add", *opts])


@arguably.command()
def commit(*, _all: bool = False):
    """
    Commit the staged changes (using amend, ie one commit per branch)

    Args:
        all: whether to add all files before committing
    """
    with pad():
        if _all:
            add("--all")
        Branch.active().commit()

    restack()


@arguably.command()
def submit(*, _force: bool = False):
    """
    Submit this branch to the remote (`s` stands for `submit`)

    Args:
        force: whether to force submit
    """
    with pad():
        _submit(_force=_force)


@arguably.command()
def submit_stack(*, _force: bool = False):
    """
    Submit this branch and its children to the remote

    Args:
        force: whether to force submit
    """
    gh = Github()
    with pad():
        traverse(
            Branch.from_head(repo().active_branch),
            lambda b: checkout_and_submit(b, _force=_force, _gh=gh),
        )


@arguably.command()
def reset():
    """
    Reset working tree to the state of the last commit
    """
    with pad():
        subprocess.run(["git", "reset", "--hard", "HEAD"])


@arguably.command()
def cs(*, _all: bool = False, _force: bool = False):
    """
    Commit all changes and submit

    Args:
        all: whether to add all files before committing
        force: whether to force submit
    """
    commit(_all=_all)
    submit(_force=_force)


@arguably.command()
def css(*, _all: bool = False, _force: bool = False):
    """
    Commit all changes and submit stack

    Args:
        all: [-a] whether to add all files before committing
        force: [-f] whether to force submit
    """
    commit(_all=_all)
    submit_stack(_force=_force)


@arguably.command()
def update(*, _force: bool = False):
    """
    Add all files, commit all changes, and submit stack

    Args:
        force: [-f] whether to force submit
    """
    with pad():
        commit(_all=True)
        submit_stack(_force=_force)


@arguably.command
def move():
    """
    Move the current branch to track a different parent
    """
    with pad():
        with not_main():
            r = repo()
            b = Branch.active()
            new_parent = questionary.select(
                f"Select a new parent for branch: {b.name}:",
                choices=[x.name for x in r.get_branches()],
            ).ask()
            with checked_out(b) as (b, _):
                b.set_upstream(new_parent)
                _restack(b)
                draw_tree_2(r, _print=True, _highlight=r.active_branch)


@arguably.command
def co(name):
    """
    Alias for `go` (`co` is short for `checkout`)

    Args:
        name: the name of the branch to go to
    """
    go(name)


@arguably.command
def r():
    """
    Alias for `restack`
    """
    restack()


@arguably.command()
def c(*, _all: bool = False):
    """
    Alias for `commit`

    Args:
        all: whether to add all files before committing
    """
    commit(_all=_all)


@arguably.command()
def s(*, _force: bool = False):
    """
    Alias for `submit`

    Args:
        force: whether to force submit
    """
    with pad():
        _submit(_force=_force)


@arguably.command()
def ss(*, _force: bool = False):
    """
    Alias for `submit-stack`

    Args:
        force: whether to force submit
    """
    with pad():
        traverse(
            Branch.from_head(repo().active_branch),
            lambda b: checkout_and_submit(b, _force=_force),
        )


@arguably.command()
def u(*, _force: bool = False):
    """
    Alias for `update`

    Args:
        force: [-f] whether to force submit
    """
    commit(_all=True)
    submit_stack(_force=_force)


def main():
    try:
        arguably.run()
    except GgException as e:
        log(str(e), _type="error")
    except git.exc.GitCommandError as e:
        log(str(e), _type="error")


if __name__ == "__main__":
    main()
