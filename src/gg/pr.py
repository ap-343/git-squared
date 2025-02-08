from .github import gh_repo
from .branch import Branch
from .exception import GgException


def create_pr():
    rr = gh_repo()
    b = Branch.active()
    if b.parent():
        # Get all open pull requests
        pull_requests = rr.get_pulls(state="open", base="main")

        # Loop through the pull requests to check the head branch
        for pr in pull_requests:
            print(pr)

        return rr.create_pull(
            title={b.head.commit.message},
            head={b.name},  # The branch with the changes
            base={b.parent().name},  # The branch you want to merge into
        )
    else:
        raise GgException("Can not create PR: No parent branch found for active branch")
