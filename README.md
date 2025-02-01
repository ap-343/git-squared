# git-squared (`gg`)

A CLI for stacked git workflows

The program is called `gg` and has the following commands:

```
% gg 
usage: gg [-h] command ...

positional arguments:
  command
    ls        List all branches and current status
    rm        Remove (delete) this branch or a named branch
    go        Go to a branch if it exists. Otherwise, create a new branch tracking the current branch.
    co        Alias for `go` (`co` is short for `checkout`)
    restack   Restack this branch and all children onto its tracking branch
    r         Alias for `restack`
    status    Show git status (alias for `git status`)
    add       Add files to the staging area (alias for `git add`)
    commit    Commit the staged changes (using amend, ie one commit per branch)
    c         Alias for `commit`
    down      Move down the tree from the current branch; ie, move to the parent branch
    up        Move up the tree from the current branch; ie, move to the child branch
    s         Submit this branch to the remote (`s` stands for `submit`)
    ss        Submit this branch and its children to the remote (`ss`stands for `submit stack`)
    reset     Reset working tree to the state of the last commit
    cs        Commit all changes and submit
    css       Commit all changes and submit stack

optional arguments:
  -h, --help  show this help message and exit
```

## install

### mac
```
brew install git-squared
```

### linux
```
pip install --user git-squared
```

## model
Stacking is a model for managing a tree of branches in a single repository.

The benefit of this approach is that you can manage many branches that are dependent on others. This helps to isolate changes and makes it easier to manage a series of related changes.

Stacking here is modeled via "upstream" or "tracking" branches. Each branch can have one upstream branch. This can be thought of as its "parent". All of this is managed automatically by `gg`. When you create a new branch using `gg create` or `gg go`, it will create a new branch and set it to track the current branch, establishing a parent/child relationship.

The _easiest_ way to work in this model is to use the "one commit per branch" approach. Again, this modeling is handled automatically if you use `gg` to commit changes. For instance, `gg commit` will create the single commit for your branch if none exists; otherwise it will amend the existing commit.

Each branch can display its status relative to its parent. The information displayed like `[0:1]` means that the branch is 0 commits behind its parent, and 1 commit ahead. This is the "happy state" of an in-progress branch. It means that the branch has all of the commits of its parent, and one new commit.

## commands

### `gg ls` shows the stack

```
% gg ls

◯          [0:0] c
◯          [0:0] b
│ ◯        [0:0] d
◯─┘        [0:0] a
│ ◯        [0:0] aaaa
│ ◯        [0:0] aaa
│ ◯        [0:0] aa
│ │ ◯      [0:0] t1
│ │ │ ◯    [0:0] t2
│ │ │ │ ◯  [0:0] t3
│ │ ◯─┴─┘  [0:1] test
│ │ │ ◯    [0:1] z
└─┴─┴─┴─●  [0:1] main

```

### `gg go` moves around the stack (or creates new branches in the stack)

```
% gg go aa

🏁 Checked out aa
         ...
│ ◯        [0:0] d
◯─┘        [0:0] a
│ ◯        [0:0] aaaa
│ ◯        [0:0] aaa
│ ●        [0:0] aa
         ...
└─┴─┴─┴─◯  [0:1] main

```

### `gg up`/`gg down` move up and down the stack

```
% gg up

🏁 Checked out aaa
         ...
│ ◯        [0:0] d
◯─┘        [0:0] a
│ ◯        [0:0] aaaa
│ ●        [0:0] aaa
│ ◯        [0:0] aa
         ...
└─┴─┴─┴─◯  [0:1] main

```

```
% gg down

🏁 Checked out aa
         ...
│ ◯        [0:0] d
◯─┘        [0:0] a
│ ◯        [0:0] aaaa
│ ◯        [0:0] aaa
│ ●        [0:0] aa
         ...
└─┴─┴─┴─◯  [0:1] main
```

