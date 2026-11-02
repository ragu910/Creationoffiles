"""File System Simulator core (Project 6): general tree + BST index by size + AVL index by name
+ symbolic-link graph with cycle detection."""
from generaltree import GeneralTree, GNode
from bst import BST
from avl import AVL
from graph import Graph
from graph_algos import find_cycle, dfs_times


def _parts(path):
    return [p for p in path.split("/") if p]


def norm(path):
    return "/" + "/".join(_parts(path))


class FileSystem:
    def __init__(self):
        self.tree = GeneralTree()
        self.size_index = BST()      # key (size, path)  -> path
        self.name_index = AVL()      # key name          -> [paths]

    # ---------- helpers ----------
    def _split(self, path):
        parts = _parts(path)
        if not parts:
            raise ValueError("path must not be the root")
        return "/" + "/".join(parts[:-1]), parts[-1]

    def _index(self, node):
        p = self.tree.path_of(node)
        if node.kind == "file":
            self.size_index.insert((node.size, p), p)
        if node.kind in ("file", "link"):
            self.name_index.insert(node.name, p)

    def _unindex(self, node, path):
        if node.kind == "file":
            self.size_index.delete((node.size, path))
        if node.kind in ("file", "link"):
            self.name_index.delete(node.name, path)

    # ---------- commands ----------
    def mkdir(self, path, parents=False):
        parts = _parts(path)
        cur = ""
        for i, name in enumerate(parts):
            parent, cur = cur or "/", cur + "/" + name
            node = self.tree.find(cur)
            if node is None:
                if i < len(parts) - 1 and not parents:
                    raise ValueError(f"parent directory not found: {parent}")
                self.tree.insert(parent, GNode(name, "dir"))
            elif node.kind != "dir":
                raise ValueError(f"{cur} exists and is not a directory")

    def create_file(self, path, size):
        parent, name = self._split(path)
        node = self.tree.insert(parent, GNode(name, "file", size=int(size)))
        self._index(node)

    def symlink(self, path, target):
        parent, name = self._split(path)
        node = self.tree.insert(parent, GNode(name, "link", target=norm(target)))
        self._index(node)

    def remove(self, path):
        removed = self.tree.delete_subtree(path)
        base = norm(path)
        for n in removed:
            # recompute the path as it was before the subtree was detached
            rel = []
            cur = n
            while cur is not None and cur is not removed[0]:
                rel.append(cur.name); cur = cur.parent
            full = base if n is removed[0] else base + "/" + "/".join(reversed(rel))
            self._unindex(n, full)
        return len(removed)

    # ---------- queries ----------
    def find_by_name(self, name):
        n = self.name_index.search(name)
        return list(n.vals) if n else []

    def files_in_size_range(self, lo, hi):
        res = self.size_index.range_query((lo, ""), (hi, "\U0010ffff"))
        return [(k[0], v) for k, v in res]

    def disk_usage(self, path="/"):
        node = self.tree.find(path)
        if node is None:
            raise ValueError(f"no such path: {path}")
        return self.tree.subtree_size(node)

    def resolve(self, path, max_hops=16):
        """Follow symbolic links. Returns (node, hops) or (None, 'loop'/'dangling')."""
        node, hops, seen = self.tree.find(path), 0, set()
        while node is not None and node.kind == "link":
            p = self.tree.path_of(node)
            if p in seen or hops >= max_hops:
                return None, "loop"
            seen.add(p); hops += 1
            node = self.tree.find(node.target)
        return (node, hops) if node is not None else (None, "dangling")

    # ---------- symbolic links as a directed graph ----------
    def link_graph(self):
        """Vertices = every node path. Edges: directory -> child, and link -> target.
        A directed cycle means that following the links can loop forever."""
        g = Graph(directed=True, weighted=False, rep="list")
        for n in self.tree.preorder_it():
            g.add_vertex(self.tree.path_of(n))
        for n in self.tree.preorder_it():
            p = self.tree.path_of(n)
            for c in n.children:
                g.add_edge(p, self.tree.path_of(c))
            if n.kind == "link" and self.tree.find(n.target) is not None:
                g.add_edge(p, n.target)
        return g

    def find_loops(self):
        """Returns (cycle as list of paths or None, list of DFS back edges as (u, v) path pairs)."""
        g = self.link_graph()
        cyc = find_cycle(g)
        _, _, _, edges = dfs_times(g)
        back = [(g.names[u], g.names[v]) for u, v, k in edges if k == "back"]
        return ([g.names[i] for i in cyc] if cyc else None), back
