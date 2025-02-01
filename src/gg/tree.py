def traverse(tree, fn):
    fn(tree)
    for child in tree.children():
        traverse(child, fn)
