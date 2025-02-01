from contextlib import contextmanager
from .log import log
from github import BadCredentialsException


@contextmanager
def github():
    try:
        yield
    # except Exception as e:
    #     print("EXCEPTION", type(e))
    except BadCredentialsException:
        log("""
[bold]:guard: You are not authenticated with Github :guard:[/bold]
            
To authenticate, please use the official Github cli: [on #EEEEEE]brew install gh[/].
            
Run the command: [on #EEEEEE]gh auth login[/] to authenticate.
            
Then try this operation again.
            """)
