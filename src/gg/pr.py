from .github import Github
from github import GithubException
from .branch import Branch
from .exception import GgException
from .log import log
from .repo import repo


# test!
def pr_exists():
    r = repo()
    b = Branch.active()
    gh = Github()
    pull_requests = gh.repo.get_pulls(state="open", base=r.main().name)

    # Loop through the pull requests to check the head branch !!
    for pr in pull_requests:
        if pr.head.ref == b.name:
            return True
    return False


def create_pr(_if_exists="noop", _if_noop="noop", _gh: Github = None):
    gh = _gh or Github()
    b = Branch.active()

    if not b.parent():
        raise GgException("Can not create PR: No parent branch found for active branch")

    if b.commits_ahead() < 1:
        if _if_noop == "noop":
            return
        raise GgException("Can not create PR: No changes to commit")

    if pr_exists():
        if _if_exists == "noop":
            return
        raise GgException("Can not create PR: PR already exists")

    try:
        return gh.repo.create_pull(
            title=b.head().commit.message,
            body="",
            head=b.name,  # The branch with the changes
            base=b.parent().name,  # The branch you want to merge into
        )
    except GithubException as e:
        log(e.data.get("eghors")[0].get("message"), _type="eghor")
