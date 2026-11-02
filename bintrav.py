"""Binary tree traversals, each both recursive and iterative (explicit stack / queue).
Works on any node with .key, .left, .right. Each returns a list of keys."""
from common import Queue


# ---------- recursive ----------
def inorder_rec(n, out=None):
    out = [] if out is None else out
    if n:
        inorder_rec(n.left, out); out.append(n.key); inorder_rec(n.right, out)
    return out


def preorder_rec(n, out=None):
    out = [] if out is None else out
    if n:
        out.append(n.key); preorder_rec(n.left, out); preorder_rec(n.right, out)
    return out


def postorder_rec(n, out=None):
    out = [] if out is None else out
    if n:
        postorder_rec(n.left, out); postorder_rec(n.right, out); out.append(n.key)
    return out


def _height_rec(n):
    return 0 if n is None else 1 + max(_height_rec(n.left), _height_rec(n.right))


def _level_rec(n, depth, target, out):
    if n is None:
        return
    if depth == target:
        out.append(n.key)
    else:
        _level_rec(n.left, depth + 1, target, out)
        _level_rec(n.right, depth + 1, target, out)


def levelorder_rec(root):
    """Recursive level order: for each level d, one recursive walk collects that level (O(n*h))."""
    out = []
    for d in range(_height_rec(root)):
        _level_rec(root, 0, d, out)
    return out


# ---------- iterative ----------
def inorder_it(root):
    out, st, cur = [], [], root
    while cur or st:
        while cur:
            st.append(cur); cur = cur.left
        cur = st.pop(); out.append(cur.key); cur = cur.right
    return out


def preorder_it(root):
    out, st = [], ([root] if root else [])
    while st:
        n = st.pop(); out.append(n.key)
        if n.right: st.append(n.right)
        if n.left: st.append(n.left)
    return out


def postorder_it(root):
    out, st, cur, last = [], [], root, None
    while cur or st:
        if cur:
            st.append(cur); cur = cur.left
        else:
            top = st[-1]
            if top.right and last is not top.right:
                cur = top.right
            else:
                out.append(top.key); last = st.pop()
    return out


def levelorder_it(root):
    out, q = [], Queue()
    if root:
        q.push(root)
    while not q.empty():
        n = q.pop(); out.append(n.key)
        if n.left: q.push(n.left)
        if n.right: q.push(n.right)
    return out


def height_it(root):
    """Number of levels, iterative (safe for degenerate trees)."""
    if root is None:
        return 0
    q, h = Queue(), 0
    q.push(root)
    while not q.empty():
        h += 1
        for _ in range(len(q)):
            n = q.pop()
            if n.left: q.push(n.left)
            if n.right: q.push(n.right)
    return h
