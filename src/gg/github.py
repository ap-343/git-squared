from contextlib import contextmanager
from .log import log
from github import BadCredentialsException
from .repo import repo
from github import Github


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


def gh_repo():
    with github():
        r = repo()
        g = Github()
        return g.get_repo(r.gh_path())
