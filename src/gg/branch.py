from .log import log
from contextlib import contextmanager
from .exception import GgException
import subprocess
from .confirm import confirm


@contextmanager
def existing_branch(name):
    b = Branch(name)
    if not b.exists():
        raise GgException(f"Branch {name} does not exist")
    yield b


class Branch:
    def __init__(self, name, _head=None):
        from .repo import repo

        self.repo = repo()
        self.name = name.replace("./", "")
        self._head = _head
        self._children = []
        self._parent = None

    @classmethod
    def from_head(cls, head):
        return cls(head.name, _head=head)

    @classmethod
    def active(cls):
        from .repo import repo

        active_head = repo().active_branch
        return cls.from_head(active_head)

    def head(self):
        if not self._head:
            self._head = self.repo.branches[self.name]
        return self._head

    def parent(self):
        if not self._parent:
            self._parent = self.tracking_branch()
        return self._parent

    def children(self):
        if not self._children:
            self._children = [
                Branch.from_head(child)
                for child in self.repo.get_branches()
                if child.tracking_branch()
                and child.tracking_branch().name == self.head().name
            ]
        return self._children

    def commit(self):
        if self.commits_ahead() > 0:
            subprocess.run(["git", "commit", "--amend", "--no-edit"])
        else:
            subprocess.run(["git", "commit"])

    def commits_behind(self):
        commits = self.repo.git.rev_list(
            f"{self.name}..{self.tracking_branch().name}"
        ).splitlines()
        behind = len(commits)
        return behind

    def commits_ahead(self):
        commits = self.repo.git.rev_list(
            f"{self.tracking_branch().name}..{self.name}"
        ).splitlines()
        ahead = len(commits)
        return ahead

    def commits_ahead_behind_message(self):
        if not self.tracking_branch():
            return ""
        ahead = self.commits_ahead()
        ahead_type = "warn" if ahead > 1 else "success" if ahead == 1 else "dim"
        behind = self.commits_behind()
        behind_type = "warn" if behind != 0 else "dim"
        msg = "[dim]:[/dim]".join(
            [
                log(str(behind), _type=behind_type, _print=False),
                log(str(ahead), _type=ahead_type, _print=False),
            ]
        )
        return f"[not bold][dim][[/dim]{msg}[dim]][/dim][/not bold]"

    def create(self, _log=True):
        b = Branch.from_head(self.repo.create_head(self.name))
        with checked_out(b, _log=False) as (b, og):
            subprocess.run(["git", "branch", "-u", og.name])
        if _log:
            log(
                f"Created branch: [bold]{self.name}[/bold] (tracking {b.tracking_branch().name})",
                _type="success",
                _emoji=":palm_tree:",
            )
        return b

    def exists(self):
        try:
            return True if self.head() else False
        except IndexError:
            return False

    def delete(self, _log=True):
        with existing_branch(self.name) as b:
            self.repo.delete_head(self.name)
            if _log:
                log(f"Deleted branch: {self.name}", _type="happy", _emoji=":knife:")

    def tracking_branch(self):
        head_tracking_branch = self.head().tracking_branch()
        return Branch.from_head(head_tracking_branch) if head_tracking_branch else None

    def checkout(self, _log=True, _create=False):
        if not self.exists() and _create:
            self.create(_log)
        if self.repo.active_branch.name == self.name:
            if _log:
                log(f"Already on [bold]{self.name}[/bold]", _type="happy")
            return
        with existing_branch(self.name) as b:
            self.repo.branches[self.name].checkout()
            if _log:
                log(
                    f"Checked out [bold]{b.name}[/bold]",
                    _type="success",
                    _emoji=":checkered_flag:",
                )


@contextmanager
def checked_out(branch: Branch, _log=False):
    from .repo import repo

    r = repo()
    og = Branch.from_head(r.active_branch)
    branch.checkout(_log)
    yield branch, og
    og.checkout(_log)


def create_new_branch(name):
    with confirm(
        log(
            f"Create new branch [bold cyan]{name}[/bold cyan] (tracking [bold cyan]{Branch.active().name}[/bold cyan])?",
            _print=False,
        )
    ) as answer:
        if answer == "y":
            Branch(name).create()
