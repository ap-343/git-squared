from contextlib import contextmanager
from .log import log
from github import BadCredentialsException, Github as Base
import subprocess
from .repo import repo


@contextmanager
def github():
    try:
        yield
    except BadCredentialsException:
        log("""
[bold]:guard: You are not authenticated with Github :guard:[/bold]
            
To authenticate, please use the official Github cli: [on #EEEEEE]brew install gh[/].
            
Run the command: [on #EEEEEE]gh auth login[/] to authenticate.
            
Then try this operation again.
            """)


class Github(Base):
    def __init__(self, *args, **kwargs):
        with github():
            token = subprocess.run(
                ["gh", "auth", "token"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ).stdout.strip()
        super().__init__(token, *args, **kwargs)

        self.repo = self.get_repo(repo().gh_path())
