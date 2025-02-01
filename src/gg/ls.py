from .log import log
import re
from rich.console import Console
from rich.tree import Tree


def plain_message(msg):
    return re.sub(r"\[.*?\]", "", re.sub(r":.*?:", " ", msg))


Tree.TREE_GUIDES = [
    ("  ", "│ ", "├-", "└-"),
    (" ", "┃ ", "┣-", "┗━"),
    (" ", "║ ", "╠═ ", "╚═"),
]


def build_message_1(repo, _branch=None, _level=0):
    max_length = 0
    _branch.message1 = "".join(
        [
            log(f"[bold]{_branch.name}[/bold]", _print=False)
            if _branch.name == repo.active_branch.name
            else "",
            log(f"{_branch.name}", _print=False)
            if _branch.name != repo.active_branch.name
            else "",
            log(
                ":round_pushpin:" if _branch.name == repo.active_branch.name else "",
                _print=False,
            ),
        ]
    )
    plain = plain_message(_branch.message1)
    max_length = max(max_length, len(plain) + _level * 2)

    for child in _branch.children():
        max_length = max(max_length, build_message_1(repo, child, _level=_level + 1))

    return max_length


def build_message_2(_branch, _max_length=None, _level=0):
    plain = plain_message(_branch.message1)
    width = len(plain) + _level * 2

    _branch.message2 = "".join(
        [
            " " * (_max_length - width),
            " " + _branch.commits_ahead_behind_message(),
        ]
    )
    for child in _branch.children():
        build_message_2(child, _max_length=_max_length, _level=_level + 1)


def build_tree(_branch, _tree=None):
    root = False
    if not _tree:
        root = True
        _tree = Tree(_branch.message1 + _branch.message2, guide_style="dim")
    for child in _branch.children():
        leaf = _tree.add(child.message1 + child.message2, guide_style="dim")
        build_tree(child, _tree=leaf)

    if root:
        return _tree


def draw_tree(repo, _branch=None):
    if not _branch:
        _branch = repo.main()

    max_length = 0
    max_length = max(max_length, build_message_1(repo, _branch))
    build_message_2(_branch, _max_length=max_length)

    tree = build_tree(_branch)
    console = Console()
    print("")
    console.print(tree)
    print("")


def last_index_of_any(s, chars):
    return (
        max(s.rfind(c) for c in chars if c in s) if any(c in s for c in chars) else -1
    )


def justify(lines):
    end_chars = ["┘", "◯", "●"]
    max_width = 0
    for line in lines:
        max_width = max(max_width, last_index_of_any(plain_message(line), end_chars))
    for i in range(len(lines)):
        end_index = last_index_of_any(lines[i], end_chars)
        end_index_plain = last_index_of_any(plain_message(lines[i]), end_chars)
        padding = max_width - end_index_plain
        lines[i] = (
            lines[i][: end_index + 1] + (" " * padding) + lines[i][end_index + 1 :]
        )
    return lines


def draw_tree_2(repo, _branch=None, _msg=[], _print=False, _slot=0, _highlight=None):
    root = not _branch
    _branch = _branch if _branch else repo.main()
    children = _branch.children()

    branch_name = _branch.name
    if branch_name == repo.active_branch.name:
        branch_name = f"[bold]{branch_name}[/bold]"

    def color_tag(msg, i):
        return f"[color({162 + (i % 10)})]{msg}[/color({162 + (i % 10)})]"

    pieces = []

    if root:
        pieces.append(color_tag("└", 0))
        for i in range(len(children) - 1):
            pieces.append(color_tag("─┴", i))
        pieces.append(
            color_tag(
                "─◯ " if _branch.name != repo.active_branch.name else "─● ",
                len(children),
            )
        )
        pieces.append(" " + _branch.commits_ahead_behind_message() + " ")
        pieces.append(color_tag(branch_name, len(children)))
        _msg = ["".join(pieces)]
    else:
        for i in range(_slot):
            pieces.append(color_tag("│ ", i))

        if len(children) > 1:
            pieces.append(
                color_tag(
                    "◯─" if _branch.name != repo.active_branch.name else "●─", _slot
                )
            )
            for i in range(len(children) - 2):
                pieces.append(color_tag("┴─", _slot + i))
            pieces.append(
                color_tag(
                    "┘ " if _branch.name != repo.active_branch.name else "┘ ",
                    _slot + len(children) - 1,
                )
            )
            pieces.append(" " + _branch.commits_ahead_behind_message() + " ")
            pieces.append(color_tag(branch_name, _slot + len(children) - 1))
        else:
            pieces.append(
                color_tag(
                    "◯ " if _branch.name != repo.active_branch.name else "● ", _slot
                )
            )
            pieces.append(" " + _branch.commits_ahead_behind_message() + " ")
            pieces.append(color_tag(branch_name, _slot))

        _msg.insert(0, "".join(pieces))

    _slot += len(children)

    while len(children):
        _slot -= 1
        child = children.pop()
        _msg = draw_tree_2(repo, _branch=child, _msg=_msg, _print=False, _slot=_slot)

    if _print:
        if _highlight:
            index = None
            for i, msg in enumerate(_msg):
                if plain_message(msg).endswith(_highlight.name):
                    index = i
                    break

            summary = [_msg[index]]
            summary_size = 2

            # add proximal rows to summary
            for i in range(summary_size):
                if index - (i + 1) >= 0:
                    summary.insert(0, _msg[index - (i + 1)])
                if index + (i + 1) < len(_msg):
                    summary.append(_msg[index + (i + 1)])

            # if index is too far away from main, add ellipsis
            if index < len(_msg) - summary_size - 2:
                summary.append(log("...", _type="dim", _print=False))

            # if main is not already included, always add it
            if index < len(_msg) - summary_size - 1:
                summary.append(_msg[len(_msg) - 1])

            # if index is too far away from top of graph, add ellipsis
            if index > summary_size:
                summary.insert(0, log("...", _type="dim", _print=False))

            log("\n".join(justify(summary)))
        else:
            log("\n".join(justify(_msg)))
    else:
        return _msg
