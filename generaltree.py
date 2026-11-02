"""Unit III - general tree for the directory hierarchy (Root -> directories -> files/links)."""
from common import Queue


class GNode:
    __slots__ = ("name", "kind", "size", "target", "children", "parent")

    def __init__(self, name, kind="dir", size=0, target=None):
        self.name, self.kind, self.size, self.target = name, kind, size, target
        self.children = []
        self.parent = None

    def label(self):
        if self.kind == "dir":
            return self.name + ("/" if self.name != "/" else "")
        if self.kind == "link":
            return f"{self.name} -> {self.target}"
        return f"{self.name} ({self.size} B)"


class GeneralTree:
    def __init__(self):
        self.root = GNode("/", "dir")

    # ----- lookup / structure -----
    def find(self, path):
        cur = self.root
        for part in [p for p in path.split("/") if p]:
            nxt = None
            for c in cur.children:
                if c.name == part:
                    nxt = c
                    break
            if nxt is None:
                return None
            cur = nxt
        return cur

    def path_of(self, node):
        parts = []
        while node is not None and node.parent is not None:
            parts.append(node.name); node = node.parent
        return "/" + "/".join(reversed(parts))

    def insert(self, parent_path, node):
        parent = self.find(parent_path)
        if parent is None or parent.kind != "dir":
            raise ValueError(f"parent directory not found: {parent_path}")
        for c in parent.children:
            if c.name == node.name:
                raise ValueError(f"'{node.name}' already exists in {parent_path}")
        node.parent = parent
        parent.children.append(node)
        return node

    def delete_subtree(self, path):
        """Detach the node at path with all descendants; returns removed nodes (preorder)."""
        node = self.find(path)
        if node is None:
            raise ValueError(f"no such path: {path}")
        if node is self.root:
            raise ValueError("cannot delete the root")
        removed = self._pre_from(node)
        node.parent.children.remove(node)
        node.parent = None
        return removed

    def _pre_from(self, start):
        out, st = [], [start]
        while st:
            n = st.pop(); out.append(n)
            for c in reversed(n.children):
                st.append(c)
        return out

    # ----- traversals: recursive -----
    def preorder_rec(self, n=None, out=None):
        n = self.root if n is None else n
        out = [] if out is None else out
        out.append(n)
        for c in n.children:
            self.preorder_rec(c, out)
        return out

    def postorder_rec(self, n=None, out=None):
        n = self.root if n is None else n
        out = [] if out is None else out
        for c in n.children:
            self.postorder_rec(c, out)
        out.append(n)
        return out

    def levelorder_rec(self):
        levels = []

        def walk(n, d):
            if len(levels) == d:
                levels.append([])
            levels[d].append(n)
            for c in n.children:
                walk(c, d + 1)
        walk(self.root, 0)
        return [n for lvl in levels for n in lvl]

    # ----- traversals: iterative -----
    def preorder_it(self):
        out, st = [], [self.root]
        while st:
            n = st.pop(); out.append(n)
            for c in reversed(n.children):
                st.append(c)
        return out

    def postorder_it(self):
        out, st = [], [(self.root, 0)]
        while st:
            n, i = st.pop()
            if i < len(n.children):
                st.append((n, i + 1)); st.append((n.children[i], 0))
            else:
                out.append(n)
        return out

    def levelorder_it(self):
        out, q = [], Queue()
        q.push(self.root)
        while not q.empty():
            n = q.pop(); out.append(n)
            for c in n.children:
                q.push(c)
        return out

    # ----- display / metrics -----
    def display(self):
        lines = []

        def walk(n, depth):
            lines.append("  " * depth + n.label())
            for c in n.children:
                walk(c, depth + 1)
        walk(self.root, 0)
        return "\n".join(lines)

    def count(self):
        return len(self.preorder_it())

    def subtree_size(self, node):
        """Total bytes below node (postorder accumulation)."""
        total = 0
        for n in self._pre_from(node):
            if n.kind == "file":
                total += n.size
        return total
