from .github import gh_repo
from github import GithubException
from .branch import Branch
from .exception import GgException
from .log import log


def pr_exists():
    b = Branch.active()
    rr = gh_repo()
    pull_requests = rr.get_pulls(state="open", base="main")

    # Loop through the pull requests to check the head branch
    for pr in pull_requests:
        if pr.head.ref == b.name:
            return True
    return False


def create_pr(_if_exists="noop"):
    rr = gh_repo()
    b = Branch.active()

    if not b.parent():
        raise GgException("Can not create PR: No parent branch found for active branch")

    if pr_exists():
        if _if_exists == "noop":
            return
        raise GgException("Can not create PR: PR already exists")

    try:
        return rr.create_pull(
            title=b.head().commit.message,
            body="body",
            head={b.name},  # The branch with the changes
            base={b.parent().name},  # The branch you want to merge into
        )
    except GithubException as e:
        log(e.data.get("errors")[0].get("message"), _type="error")
